# Quinhão

**English** · [Português](README.pt.md) · [Français](README.fr.md)

> *Quinhão* (Portuguese): the share that is owed to someone by right.

Mozambican law directs **2.75%** of the tax on mining and petroleum production to the
communities that host those operations. The money is transferred. What nobody can tell
you is **why your community received that particular amount**, or **what was built with it**.

This is not an accusation — it is the finding of Mozambique's own transparency body.
From the EITI Mozambique report:

> "o REOE não permite aferir qual foi o critério utilizado para repartir o valor a alocar
> para cada comunidade e para quais actividades os fundos foram alocados"
>
> *("the budget execution report does not allow us to determine what criterion was used to
> split the amount allocated to each community, nor what activities the funds went to")*

Quinhão turns six years of those transfers into something a person in Nyamanhumbir or
Benga can actually read, compare, and question.

## What this repository contains today

A verified data pipeline. The application is not built yet.

| File | Contents |
|---|---|
| `src/extract.py` | Downloads the source PDFs from eiti.org and parses them |
| `data/transfers.csv` | 129 rows — allocation vs. realisation per locality, 2019/2021/2023/2024 |
| `data/projects.csv` | 41 rows — individual funded projects with amounts, 2022 (**draft**, see caveats) |

### The six-year series

| Year | Source | Granularity | Total (million MZN) |
|---|---|---|---|
| 2019 | 2020 EITI Report, Table 42 | locality | 88.0 allocated / 87.8 realised |
| 2021 | 2021 EITI Report, Table 46 | locality | 73.4 |
| 2022 | 2022 EITI Report, Table 45 | **individual project** | 44.6 |
| 2023 | 2023–2024 EITI Report, Annex 6.1 | locality + mineral | 77.1 |
| 2024 | 2023–2024 EITI Report, Annex 6.1 | locality + mineral | 318.7 |

Every figure traces back to a public PDF published by [eiti.org](https://eiti.org/countries/mozambique).
No number in this repository was typed by hand.

## Running it

Requires Python 3.9+ and `pdftotext` (poppler). No Python packages to install.

```bash
brew install poppler          # macOS
sudo apt install poppler-utils # Debian/Ubuntu
```

```bash
python3 src/extract.py
```

The script downloads ~25 MB of source PDFs into `data/raw/` on first run, caches them,
and regenerates both CSVs. It ends with a self-check that asserts each year's parsed
total equals the published total — **if a parser drifts, the run fails loudly** rather
than writing wrong numbers.

## Data caveats

Read these before using the data. They are the point, not the fine print.

- **`projects.csv` (2022) is a draft.** The amounts are reliable — they sum to the
  published total of 44,608,666.89 MZN exactly. The province/district/community labels
  and the project descriptions are **not**: the source PDF merges those cells vertically
  and wraps descriptions above and below their own amount. Every row carries
  `needs_review=yes` until someone checks the 41 rows against the PDF by hand.
- **Allocation is not delivery.** Both the annexes and the reports state realisation at
  ~100% of allocation. That means the money left the treasury, not that anything was
  built. Field verification is the missing layer.
- **Two-year lag.** Funds released in a given year are based on revenue collected two
  years earlier (n−2). The 2021 allocation reflects 2019 revenue.
- **The 2.75% is not applied to the whole tax base.** The 2020 report shows 2.75% of the
  2018 production tax should have been 100.59 million MZN; 87.8 million was allocated —
  a 12.79 million gap. The Ministry's explanation is that only the *mining* production
  tax counts, not the petroleum one.
- **Locality names drift between years.** Topuito is filed under Moma in 2019 and under
  Larde from 2021. Spellings vary (`Micaune`/`Micaúne`, `Ilmenite`/`Iimenite`). Names
  are reproduced as published, not normalised.
- **Values are in millions of MZN** in `transfers.csv` and in full meticais in
  `projects.csv`, matching their respective sources.

## Sources

- [EITI Mozambique country page](https://eiti.org/countries/mozambique) — all reports and annexes
- Annex 6.1, Transfers to communities (2023–2024 report)
- Tables 42, 45 and 46 of the 2020, 2022 and 2021 reports
- [Centro de Integridade Pública](https://www.cipmoz.org/) — independent analysis of the 2.75%

## Context

Built for the Open Society Foundations × Andela hackathon, *Information You Can Trust*,
**Transparency & Accountability** track.

Code and identifiers are in English. User-facing content is in English, Portuguese and
French. Portuguese is the language of the source documents and of the Mozambican state;
a local-language edition (Emakhuwa is spoken across Montepuez, Balama, Ancuabe, Topuito
and Moma — the localities that receive the most) requires a native speaker and is not
machine-translated here.

## Licence

Code: MIT. The underlying data is published by EITI Mozambique and is public.
