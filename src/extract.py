"""Extract the 2.75% extractive-revenue community transfers from Mozambique EITI reports.

Sources are PDFs published by eiti.org. Text is extracted with `pdftotext -layout`
(poppler-utils), then parsed per year because the table layout changes every year.

Outputs:
  data/transfers.csv  - allocation vs realisation per locality (2019, 2021, 2023, 2024)
  data/projects.csv   - individual funded projects with amounts (2022)

Run: python3 src/extract.py
"""

import csv
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# EITI document ids -> local filename. Redirects to the real PDF.
SOURCES = {
    "annex_6.1_communities_2023_2024": "https://eiti.org/document/26172",
    "report_2022": "https://eiti.org/document/24717",
    "report_2021": "https://eiti.org/document/23064",
    "report_2020": "https://eiti.org/document/21672",
}

PROVINCES = [
    "Niassa", "Cabo Delgado", "Nampula", "Zambezia", "Zambézia", "ZambEzia",
    "Tete", "Manica", "Sofala", "Inhambane", "Inhanbane", "Gaza", "Maputo",
]


def fetch(name, url):
    """Download a source PDF once and return its extracted text."""
    pdf = RAW / f"{name}.pdf"
    txt = RAW / f"{name}.txt"
    if not pdf.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"downloading {name}...")
        # eiti.org rejects the default urllib User-Agent with a 403.
        req = urllib.request.Request(url, headers={"User-Agent": "quinhao-etl/1.0"})
        with urllib.request.urlopen(req) as resp:
            pdf.write_bytes(resp.read())
    if not txt.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
    return txt.read_text(encoding="utf-8", errors="replace")


def num(s):
    """'1.234,56' and '0,1' are Portuguese decimals; '' and '-' are missing."""
    s = s.strip()
    if not s or s in {"-", "—"}:
        return None
    return float(s.replace(".", "").replace(",", "."))


def is_province(label):
    return label.strip() in PROVINCES


# --- 2023 & 2024: Annex 6.1, richest layout -------------------------------
# district | locality | mining activity | alloc23 real23 %23 | alloc24 real24 %24
ROW_6NUM = re.compile(r"^\s*(.*?)\s{2,}((?:[\d.,]+\s+){5}[\d.,]+)\s*$")


def parse_annex_61(text):
    rows, total = [], {}
    province = district = None
    for line in text.splitlines():
        m = ROW_6NUM.match(line)
        if not m:
            # A district name can sit alone on a line when it wraps (e.g. "Mocimboa da Praia").
            bare = line.strip()
            if bare and not any(c.isdigit() for c in bare) and len(bare.split("  ")) == 1:
                district = bare
            continue
        labels = [p.strip() for p in re.split(r"\s{2,}", m.group(1).strip()) if p.strip()]
        n = [num(v) for v in m.group(2).split()]
        if labels and labels[0].lower().startswith("total"):
            total = {2023: n[0], 2024: n[3]}
            continue
        if not labels:
            continue
        if is_province(labels[0]):
            province, district = labels[0], None  # subtotal row; only the label matters
            continue
        if len(labels) >= 3:
            district, locality, activity = labels[0], labels[1], labels[2]
        elif len(labels) == 2:
            district, locality, activity = labels[0], labels[1], ""
        else:
            locality, activity = labels[0], ""  # locality inherits the district above
        for year, alloc, real in ((2023, n[0], n[1]), (2024, n[3], n[4])):
            rows.append({
                "year": year, "province": province, "district": district,
                "locality": locality, "mining_activity": activity,
                "allocated_mzn_m": alloc, "realised_mzn_m": real,
            })
    return rows, total


# --- 2019 & 2021: in-report tables, district cell merged vertically --------
ROW_2NUM = re.compile(r"^\s*(.*?)\s{2,}([\d.,]+)\s+([\d.,]+)\s*$")


def parse_inline_table(text, start_marker, end_marker, year):
    chunk = text.split(start_marker, 1)[-1].split(end_marker, 1)[0]
    rows, total, province, district = [], None, None, None
    for line in chunk.splitlines():
        m = ROW_2NUM.match(line)
        if not m:
            bare = line.strip()
            if bare and not any(c.isdigit() for c in bare) and len(bare) < 40:
                district = bare
            continue
        labels = [p.strip() for p in re.split(r"\s{2,}", m.group(1).strip()) if p.strip()]
        alloc, real = num(m.group(2)), num(m.group(3))
        if not labels:
            continue
        if labels[0].lower().startswith("total"):
            total = alloc
            continue
        if is_province(labels[0]):
            province, district = labels[0], None
            continue
        if len(labels) >= 2:
            district, locality = labels[0], labels[1]
        else:
            locality = labels[0]
        rows.append({
            "year": year, "province": province, "district": district,
            "locality": locality, "mining_activity": "",
            "allocated_mzn_m": alloc, "realised_mzn_m": real,
        })
    return rows, total


# --- 2022: project-level table, columns are positional --------------------
# Column starts in the source layout: province <18, district 18-35,
# community 36-43, description >=44. The money column is last on the line.
DESC_COL, DISTRICT_COL, COMMUNITY_COL = 44, 18, 36
MONEY = re.compile(r"([\d]{1,3}(?:\.\d{3})*,\d{2})\s*$")
# The running page header is printed straight through the table body.
FURNITURE = re.compile(r"Iniciativa de Transpar\u00eancia na Ind\u00fastria Extractiva\s*\u2502I2A Consultoria(?: e)? Servi\u00e7os")


def _fields(line):
    """[(start_column, text)] for each run separated by two or more spaces."""
    return [(m.start(), m.group().strip()) for m in re.finditer(r"\S(?:.*?\S)?(?=\s{2,}|$)", line)]


def parse_projects_2022(text):
    """Parse the 2022 project table into one row per funded project.

    Amounts are reliable: they sum to the published total exactly. Labels and
    descriptions are NOT - the source merges province/district/community cells
    vertically and wraps descriptions above and below their amount, so every row
    ships with needs_review=yes and this file is a draft pending a manual pass.

    ponytail: 41 rows in a document that will never be republished. Hand-check them
    once rather than hardening this parser. Upgrade path if it ever matters:
    pdfplumber word coordinates instead of flattened `pdftotext -layout` output.
    """
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if "Projecto/Actividades" in l)
    rows, pending = [], []
    province = district = community = ""
    for i in range(start + 1, len(lines)):
        line = FURNITURE.sub(lambda m: " " * len(m.group()), lines[i])
        if "Total Geral" in line:
            break
        if not line.strip() or "Subtotal" in line or "Projecto/Actividades" in line:
            continue
        fields = _fields(line)
        desc = " ".join(t for c, t in fields if c >= DESC_COL and not MONEY.fullmatch(t))
        labels = [(c, t) for c, t in fields if c < DESC_COL]
        for c, t in labels:
            if c < DISTRICT_COL:
                province = t
            elif c < COMMUNITY_COL:
                district = t
            else:
                community = t
        money = MONEY.search(line)
        if not money:
            if desc:
                pending.append(desc)
            continue
        body = MONEY.sub("", desc).strip()
        rows.append({
            "year": 2022, "province": province, "district": district,
            "community": community,
            "project": " ".join(x for x in pending + [body] if x),
            "amount_mzn": num(money.group(1)),
            "needs_review": "yes",  # labels unverified; see docstring
        })
        pending = []
    return rows


# --- assembly -------------------------------------------------------------
# Published totals, in millions of MZN except 2022 which is in full meticais.
# These are the self-check: if a parser drifts, the run fails loudly.
PUBLISHED_TOTALS = {2019: 88.0, 2021: 73.4, 2022: 44_608_666.89, 2023: 77.1, 2024: 318.7}

TRANSFER_FIELDS = ["year", "province", "district", "locality", "mining_activity",
                   "allocated_mzn_m", "realised_mzn_m"]
PROJECT_FIELDS = ["year", "province", "district", "community", "project",
                  "amount_mzn", "needs_review"]


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main():
    texts = {name: fetch(name, url) for name, url in SOURCES.items()}

    transfers, totals = parse_annex_61(texts["annex_6.1_communities_2023_2024"])
    rows_21, total_21 = parse_inline_table(
        texts["report_2021"], "Província & Distrito", "Tabela 46 - Alocação dos 2,75%", 2021)
    rows_19, total_19 = parse_inline_table(
        texts["report_2020"], "Province & District", "Table 42 - Allocation of 2,75%", 2019)
    transfers += rows_21 + rows_19
    projects = parse_projects_2022(texts["report_2022"])

    found = {2023: totals.get(2023), 2024: totals.get(2024), 2021: total_21,
             2019: total_19, 2022: round(sum(r["amount_mzn"] for r in projects), 2)}
    for year, expected in PUBLISHED_TOTALS.items():
        got = found[year]
        assert got is not None and abs(got - expected) < 0.01, \
            f"{year}: parsed total {got} != published {expected}"
    print("self-check: all 5 yearly totals match the published figures")

    transfers.sort(key=lambda r: (r["year"], r["province"] or "", r["locality"] or ""))
    write_csv(ROOT / "data" / "transfers.csv", TRANSFER_FIELDS, transfers)
    write_csv(ROOT / "data" / "projects.csv", PROJECT_FIELDS, projects)


if __name__ == "__main__":
    main()
