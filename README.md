# 🎬 Saudi Box Office 2020–2026: What Will Grow a Flat Market?

> **Status:** 🚧 In progress: data collection phase

## The business problem

Since cinemas reopened in 2018, Saudi Arabia has become the largest box office in the Middle East. But since 2022, annual revenue has **stayed around SR 900M** (SR 937M in 2022 → SR 922M → SR 845.6M → SR 920.8M in 2025), even though new screens keep opening.

**If I were advising a cinema operator or the Film Commission: what can grow the market?**

## Questions

| # | Lens | Question | Why it matters |
|---|------|----------|----------------|
| 1 | **Content** | Are Saudi films *growing* the market, or *taking share* from foreign films? | Decides whether investing in local content brings new audiences or just moves revenue between films |
| 2 | **Location** | Which cities have more demand than screens? | Tells operators where to open next |
| 3 | **Timing** | When does demand peak and dip (Ramadan, Eid, summer, Riyadh Season)? | Release scheduling, staffing, pricing & promotions |

## Data

| Source | What | Granularity |
|---|---|---|
| Saudi Film Commission weekly box office | Market revenue, tickets, top films | Weekly |
| Saudi Film Commission annual reports | Revenue by country of production, by city | Yearly |
| Umm Al-Qura calendar + news | Ramadan, Eids, Riyadh Season, COVID closure | Events |

No ready-made dataset exists. **I collected the data myself** from official reports and press coverage. Every row has a `source_url`.

## Tools

`Python (pandas)` → cleaning & validation · `SQL (SQLite)` → analysis · `Power BI` → dashboard · `matplotlib` → README charts

## Project structure

```
saudi-box-office/
├── data/
│   ├── raw/saudi_box_office_collection.xlsx   ← manual data collection (source of truth)
│   └── processed/                             ← clean CSVs + cinema.db (generated)
├── notebooks/
│   └── 01_load_and_validate.ipynb             ← clean, validate, load into SQLite
├── sql/
│   ├── schema.sql                             ← table definitions
│   └── analysis.sql                           ← queries for each question
├── dashboard/                                 ← Power BI file + screenshots
└── reports/figures/                           ← charts used below
```

## How to run

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_load_and_validate.ipynb   # run all cells
# then open data/processed/cinema.db in DB Browser for SQLite and run sql/analysis.sql
```

## Findings

_Coming soon._

## Recommendations

_Coming soon._

## Limitations

- Data is collected by hand from public reports, so some weeks may be missing.
- Revenue by cinema operator is not public, so the city analysis uses screens instead.
- Streaming (Shahid, Netflix) may affect cinema demand, but there's no Saudi-only subscriber data to test this.
- Ramadan/Eid weeks and big Saudi releases often overlap, so their effects are hard to separate.

---
*By Ghadi *
