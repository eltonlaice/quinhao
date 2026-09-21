# Written summary — Quinhão

**Live page:** https://eltonlaice.github.io/quinhao/
**Repository:** https://github.com/eltonlaice/quinhao

## Track

**Transparency & Accountability.** Quinhão makes a specific government decision visible
and open to scrutiny: how much of Mozambique's mining and petroleum production tax
reaches the communities that host the extraction, and what happened to it after that.

Mozambican law directs 2.75% of that tax to those communities. The money is transferred
and reported as fully executed. What is missing is anything a resident can act on — why
their locality received that particular amount, and whether anything was built with it.

## The information sources

Everything on the page comes from documents published by **EITI Mozambique** at eiti.org.
Five source PDFs, covering six fiscal years:

| Year | Source | Granularity |
|---|---|---|
| 2019 | 2020 EITI Report, Table 42 | locality |
| 2021 | 2021 EITI Report, Table 46 | locality |
| 2022 | 2022 EITI Report, Table 45 | individual project |
| 2023–2024 | 2023–2024 EITI Report, Annexes 6.1 and 6.2 | locality + commodity; provincial directorates |

Two supporting sources: administrative boundaries from **geoBoundaries** (ADM1 and ADM2,
gbOpen), and official annual average exchange rates from the **World Bank**
(indicator PA.NUS.FCRF) for the metical/dollar toggle.

## Approach to trust and accuracy

The subject is the credibility of public numbers, so the tool cannot ask to be trusted —
it has to be checkable.

**Nothing is typed by hand.** `src/extract.py` downloads each source PDF and parses it.
The two CSVs in `data/` are build outputs, not manual transcription.

**The build fails rather than publishes a wrong number.** After parsing, the script
asserts each year's computed total against the total printed in the source: 88.0, 73.4,
44,608,666.89, 77.1 and 318.7. If a parser drifts, the run stops. The same applies to the
provincial annex (840.30) and to the map: a district name that does not match a polygon
fails the build instead of silently disappearing from the map. That check caught two real
errors — `Alto Moloucue` vs `Alto Molocue`, and Pemba filed as "Cidade De Pemba".

**Corrections are explicit and auditable.** The source PDFs merge district cells
vertically and centre text inside them, so column position cannot always tell a
(district, locality) pair from a (locality, activity) one. Rather than hide a fuzzy
heuristic, the affected rows are listed in a `CORRECTIONS` table in the code, with the
reason stated.

**Currency conversion is per year, not at today's rate.** The metical moved from 62.55
to 69.47 to 63.91 per dollar over this period; converting 2019 figures at a 2024 rate
would misstate them by about a tenth.

**What the data cannot show is stated on the page, not buried.** Allocation is reported
at ~100% execution, which means the money left the treasury — not that anything was
built. The 2022 project-level file ships as a draft because its labels are unreliable.
And the strongest finding is EITI's own sentence, quoted directly: the budget execution
report does not allow anyone to determine what criterion split the money between
communities.

## What the tool does with that

- The national picture: 318.7 million MZN to affected communities in 2024, against
  840.3 million to provincial directorates.
- A six-year series showing a 39% fall in 2022 and a quadrupling in 2024, neither
  explained in the reports.
- Province and district choropleths with a year filter, which show how concentrated the
  money is — 86.7 of Tete's 98.0 million goes to a single district, Moatize.
- A locality lookup covering 56 localities: what arrived, per year, from which commodity.
- For each one, the **next step**: the District Secretariat and the Locality Consultative
  Council are answerable for the money, the law limits it to four areas, and three
  specific questions a resident has the right to ask.

Three languages (English, Portuguese, French) and two currencies. The whole page is one
80 KB file with no external requests, no fonts and no frameworks, so it loads on a weak
connection and keeps working offline once opened.

## How AI coding tools were used

Claude Code was used throughout, and the most valuable work was not writing code.

**Killing the original idea.** The first concept was "allocated versus actually
transferred". Reading the source annexes showed execution reported at 100% across the
board — that story did not exist. The finding that replaced it (the split criterion is
undeterminable, and communities receive a third of what provincial directorates do) came
out of the documents, not out of a prompt.

**PDF archaeology.** Locating the community-transfer tables across five reports with
three different layouts, and discovering that the 2022 report publishes project-level
spending, was iterative reading — the kind of search that is slow by hand.

**Parser development against a hard check.** Each per-year parser was written, run, and
corrected against the published totals until all five matched. Several bugs surfaced only
because the assertion failed.

**Verification.** The live page was driven in a browser at phone width, in all three
languages, and the chart palette was run through a colourblind-safety validator rather
than chosen by eye.

**What was checked rather than trusted.** Data availability for both candidate ideas was
verified before committing — the national procurement portal turned out to be returning a
database error, which is why this project uses EITI data instead. A photograph offered
for the page was rejected because it showed an offshore oil platform of a type Mozambique
does not have.

## Limits

The 2022 project file needs a manual pass over 41 rows. There is no field-verification
layer yet — that is the natural next step, and the reason the page ends with questions a
resident can take to the District Secretariat. The method ports directly to any of the
50+ EITI implementing countries, since the reporting format is the same.
