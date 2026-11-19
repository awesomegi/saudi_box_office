import json

cells = []
def md(s): cells.append({"id": f"c{len(cells)}", "cell_type": "markdown", "metadata": {}, "source": s.strip("\n")})
def code(s): cells.append({"id": f"c{len(cells)}", "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n")})

md("""
# 01 · Load, clean & validate

**Goal:** turn the collection workbook into clean tables + a SQLite database.

`data/raw/saudi_box_office_collection.xlsx` → clean → `data/processed/*.csv` + `data/processed/cinema.db`

Run top to bottom. Every **⚠️** line is something to fix in the workbook, then re-run.
""")

code("""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW = ROOT / "data/raw/saudi_box_office_collection.xlsx"
OUT = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)

TABLES = ["weekly_box_office", "weekly_top_films", "annual_summary",
          "annual_by_country", "annual_by_city", "calendar_events"]

raw = pd.read_excel(RAW, sheet_name=TABLES)
for name, df in raw.items():
    print(f"{name:20s} {df.shape}")
""")

md("""
## 1. Generic cleaning
- drop fully empty rows (the template has blank formatted rows)
- drop the example row if you left the word EXAMPLE in `notes`
- trim spaces in text columns
- drop helper formula columns from the workbook (we recompute in SQL)
""")

code("""
HELPER_COLS = ["implied_avg_price_check", "revenue_per_screen"]

def basic_clean(df):
    df = df.dropna(how="all").copy()
    df = df.drop(columns=[c for c in HELPER_COLS if c in df.columns])
    if "notes" in df.columns:
        df = df[~df["notes"].astype(str).str.contains("EXAMPLE", na=False)]
    for c in df.select_dtypes(include=["object", "string"]):
        df[c] = df[c].astype(str).str.strip().replace({"nan": pd.NA, "": pd.NA, "None": pd.NA})
    return df

clean = {name: basic_clean(df) for name, df in raw.items()}
for name, df in clean.items():
    print(f"{name:20s} {len(df):>5} rows")
""")

md("## 2. Fix types (dates, numbers)")

code("""
DATE_COLS = {"weekly_box_office": ["week_start", "week_end"],
             "weekly_top_films": ["week_start"],
             "calendar_events": ["start_date", "end_date"]}
NUM_COLS = ["total_revenue_sar", "tickets_sold", "films_screened", "rank",
            "weekly_revenue_sar", "weekly_tickets", "cumulative_revenue_sar",
            "avg_ticket_price_sar", "cinemas", "screens", "cities",
            "revenue_share_pct", "num_films", "revenue_sar", "year"]

for name, df in clean.items():
    for c in DATE_COLS.get(name, []):
        bad = pd.to_datetime(df[c], errors="coerce").isna() & df[c].notna()
        if bad.any():
            print(f"⚠️ {name}.{c}: unreadable dates →", df.loc[bad, c].tolist())
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    for c in NUM_COLS:
        if c in df.columns:
            before = df[c].notna()
            df[c] = pd.to_numeric(df[c], errors="coerce")
            bad = before & df[c].isna()
            if bad.any():
                print(f"⚠️ {name}.{c}: not a number →", raw[name].loc[bad[bad].index, c].tolist())
print("types done")
""")

md("""
## 3. Validation checks
Each check prints ⚠️ with the rows to fix. **No output = good.**
""")

code("""
def warn(cond, msg, df):
    if cond.any():
        print(f"⚠️ {msg} ({cond.sum()} rows)")
        display(df[cond])

w = clean["weekly_box_office"]
if len(w):
    warn(w["week_start"].duplicated(keep=False), "duplicate weeks", w)
    warn(pd.to_datetime(w["week_end"]) < pd.to_datetime(w["week_start"]), "week_end before week_start", w)
    warn(w["total_revenue_sar"] < 1_000_000, "weekly revenue < SR1M (typo? wrote 16 instead of 16000000?)", w)
    price = w["total_revenue_sar"] / w["tickets_sold"]
    warn((price < 25) | (price > 90), "implied ticket price outside SR25–90", w)
    # missing weeks
    weeks = pd.to_datetime(w["week_start"]).sort_values()
    gaps = weeks.diff().dt.days
    if (gaps > 7).any():
        print(f"ℹ️ {int((gaps > 7).sum())} gaps in weekly data, e.g.:", weeks[gaps > 7].dt.date.head().tolist())

t = clean["weekly_top_films"]
if len(t):
    warn(t.duplicated(["week_start", "film_title"], keep=False), "same film twice in a week", t)
    warn(~t["is_saudi"].isin(["Y", "N"]), "is_saudi must be Y or N", t)
    warn((t["is_saudi"] == "Y") != (t["country_of_production"] == "Saudi Arabia"),
         "is_saudi doesn't match country_of_production", t)

a = clean["annual_summary"]
p = a["total_revenue_sar"] / a["tickets_sold"]
warn((p - a["avg_ticket_price_sar"]).abs() > 2, "revenue/tickets ≠ reported avg price (±2 SAR)", a)

c = clean["annual_by_country"]
share = c.groupby("year")["revenue_share_pct"].sum()
for y, s in share.items():
    if s > 1.01:
        print(f"⚠️ annual_by_country {y}: shares add to {s:.1%} (>100%). Did you type 58.5 instead of 0.585?")
""")

md("## 4. Derived columns")

code("""
# Fill revenue_sar from share × annual total when the report gave only %
c = clean["annual_by_country"].merge(
    clean["annual_summary"][["year", "total_revenue_sar"]], on="year", how="left")
c["revenue_sar"] = c["revenue_sar"].fillna(c["revenue_share_pct"] * c["total_revenue_sar"])
clean["annual_by_country"] = c.drop(columns="total_revenue_sar")

# Standardise film titles a bit (same film, different spellings is the #1 problem in this data)
t = clean["weekly_top_films"]
if len(t):
    t["film_title"] = t["film_title"].str.title()
    print("Titles to eyeball for duplicates:")
    print(t["film_title"].value_counts().head(30))
clean["annual_by_country"].head()
""")

md("## 5. Save → CSV + SQLite")

code("""
db_path = OUT / "cinema.db"
con = sqlite3.connect(db_path)
con.executescript((ROOT / "sql/schema.sql").read_text())

for name, df in clean.items():
    df.to_csv(OUT / f"{name}.csv", index=False)
    df.to_sql(name, con, if_exists="append", index=False)

for name in TABLES:
    n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"{name:20s} {n:>5} rows in DB")
""")

md("## 6. Sanity check: first look at the headline")

code("""
pd.read_sql('''
    SELECT year,
           ROUND(total_revenue_sar/1e6,1) AS revenue_m_sar,
           ROUND(tickets_sold/1e6,1)      AS tickets_m,
           avg_ticket_price_sar
    FROM annual_summary
    WHERE total_revenue_sar IS NOT NULL
    ORDER BY year
''', con)
""")

code("con.close()")

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
for c in nb["cells"]:
    c["source"] = c["source"].splitlines(keepends=True)
json.dump(nb, open("notebooks/01_load_and_validate.ipynb", "w"), indent=1, ensure_ascii=False)
print("ok")
