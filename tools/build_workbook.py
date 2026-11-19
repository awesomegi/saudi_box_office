from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

F = "Arial"
HEAD = PatternFill("solid", fgColor="1F3A5F")
INPUT = PatternFill("solid", fgColor="FFF8DC")
EX = PatternFill("solid", fgColor="E8F0E0")
thin = Side(style="thin", color="CCCCCC")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
BLUE = Font(name=F, color="0000FF")
N = Font(name=F)

wb = Workbook()

# ---------- README ----------
ws = wb.active
ws.title = "README"
lines = [
    ("Saudi Box Office: Data Collection Workbook", Font(name=F, bold=True, size=14)),
    ("", N),
    ("How to use", Font(name=F, bold=True, size=12)),
    ("1. Each tab = one table. Column names match the SQL tables in sql/schema.sql. Don't rename them.", N),
    ("2. Row 2 on every data tab is an EXAMPLE row (green). Replace or delete it once you add real data.", N),
    ("3. Cream-coloured cells are where you type. Blue text = a number you entered by hand.", N),
    ("4. Always fill source_url, so every number can be traced back.", N),
    ("5. Money is in SAR. Write 16000000, not '16M' or '16 million'.", N),
    ("6. Dates as YYYY-MM-DD.", N),
    ("7. When a tab is done: the notebook 01_load_and_validate.ipynb reads this file directly.", N),
    ("", N),
    ("Where to find the data", Font(name=F, bold=True, size=12)),
    ("Weekly figures: Saudi Film Commission weekly box office posts (film.moc.gov.sa, their X account), and news (Arab News, Saudi Gazette, Argaam, Al Eqtisadiah).", N),
    ("Annual figures: Saudi Film Commission annual box office reports (by country of production, by city).", N),
    ("Cross-check: Box Office Mojo Saudi pages are incomplete. Use them only to spot gaps.", N),
    ("", N),
    ("Pre-filled annual rows", Font(name=F, bold=True, size=12)),
    ("Some annual numbers are pre-filled from news coverage of Film Commission reports. Each has its source_url. Verify against the original report when you can.", N),
    ("Ramadan/Eid dates in calendar_events are approximate (±1 day). Check them against the Umm Al-Qura calendar.", N),
    ("", N),
    ("Tabs", Font(name=F, bold=True, size=12)),
    ("weekly_box_office: one row per week, market totals → Q3 seasonality", N),
    ("weekly_top_films: one row per film per week → Q1 Saudi vs foreign films", N),
    ("annual_summary: one row per year → the 'flat market' headline", N),
    ("annual_by_country: revenue share by country of production → Q1", N),
    ("annual_by_city: revenue/tickets/screens by city → Q2", N),
    ("calendar_events: Ramadan, Eids, Riyadh Season, holidays → Q3", N),
    ("Roadmap: your project tracker", N),
]
for i, (t, f) in enumerate(lines, 1):
    ws.cell(row=i, column=1, value=t).font = f
ws.column_dimensions["A"].width = 130

def sheet(name, cols, example, rows=200, widths=None, comments=None, extra=None):
    s = wb.create_sheet(name)
    for c, h in enumerate(cols, 1):
        cell = s.cell(row=1, column=c, value=h)
        cell.font = Font(name=F, bold=True, color="FFFFFF")
        cell.fill = HEAD
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = BOX
        s.column_dimensions[cell.column_letter].width = (widths or {}).get(h, 18)
        if comments and h in comments:
            cell.comment = Comment(comments[h], "Template")
    all_rows = [example] + (extra or [])
    for r, vals in enumerate(all_rows, 2):
        for c, v in enumerate(vals, 1):
            cell = s.cell(row=r, column=c, value=v)
            cell.fill = EX if r == 2 else INPUT
            cell.font = BLUE if isinstance(v, (int, float)) and not isinstance(v, bool) else N
            cell.border = BOX
    for r in range(len(all_rows) + 2, rows + 2):
        for c in range(1, len(cols) + 1):
            cell = s.cell(row=r, column=c)
            cell.fill = INPUT
            cell.font = BLUE
            cell.border = BOX
    s.freeze_panes = "A2"
    return s

# ---------- weekly_box_office ----------
s = sheet("weekly_box_office",
    ["week_start", "week_end", "total_revenue_sar", "tickets_sold", "films_screened", "source_url", "notes"],
    ["2026-09-13", "2026-09-19", 16000000, 329200, 59,
     "https://www.arabnews.pk/saudi-arabia/saudi-films-cross-sr100m-for-second-year-as-local-cinema-gains-ground-3001897",
     "EXAMPLE row (real figures). Keep or replace."],
    widths={"source_url": 45, "notes": 35},
    comments={"total_revenue_sar": "Whole market that week, in SAR. Full number, e.g. 16000000.",
              "week_start": "Film Commission weeks usually run Sat→Fri. YYYY-MM-DD."})
for r in range(2, 202):
    s.cell(row=r, column=3).number_format = "#,##0"
    s.cell(row=r, column=4).number_format = "#,##0"

# ---------- weekly_top_films ----------
s = sheet("weekly_top_films",
    ["week_start", "rank", "film_title", "country_of_production", "is_saudi", "age_rating",
     "weekly_revenue_sar", "weekly_tickets", "cumulative_revenue_sar", "source_url"],
    ["2025-07-13", 2, "Al-Zarfa", "Saudi Arabia", "Y", "", None, None, 22600000,
     "https://www.zawya.com/en/business/technology-and-telecom/saudi-films-earn-2666mln-at-box-office-in-2025-eaotcmki"],
    rows=800,
    widths={"film_title": 28, "country_of_production": 22, "source_url": 45},
    comments={"country_of_production": "Use the same spelling every time: Saudi Arabia, Egypt, USA, India, UK, Japan, Other.",
              "is_saudi": "Y or N",
              "age_rating": "e.g. G, PG12, PG15, R18. Leave blank if the source doesn't say.",
              "cumulative_revenue_sar": "Total since release, if reported."})
dv = DataValidation(type="list", formula1='"Y,N"', allow_blank=True)
s.add_data_validation(dv); dv.add("E2:E801")
dv2 = DataValidation(type="list", formula1='"Saudi Arabia,Egypt,USA,India,UK,Japan,Other"', allow_blank=True)
s.add_data_validation(dv2); dv2.add("D2:D801")
for r in range(2, 802):
    for c in (7, 8, 9):
        s.cell(row=r, column=c).number_format = "#,##0"

# ---------- annual_summary ----------
U1 = "https://www.argaam.com/en/article/articledetail/id/1895292"
U2 = "https://www.scenenow.com/Buzz/Saudi-Cinema-Ticket-Revenues-Surpass-SAR-845-Million-in-2024"
U3 = "https://saudigazette.com.sa/article/651384"
s = sheet("annual_summary",
    ["year", "total_revenue_sar", "tickets_sold", "films_screened", "avg_ticket_price_sar",
     "implied_avg_price_check", "cinemas", "screens", "cities", "source_url"],
    [2025, 920800000, 18800000, 538, 49, None, None, None, None, U1],
    rows=12,
    widths={"source_url": 45, "implied_avg_price_check": 22},
    comments={"implied_avg_price_check": "Formula: revenue / tickets. Should be close to avg_ticket_price_sar. A big gap = typo."},
    extra=[
        [2024, 845600000, 17500000, 504, 48.2, None, None, None, None, U2],
        [2023, 922000000, None, None, None, None, None, None, None, U3],
        [2022, 937000000, None, None, None, None, None, None, None, U3],
        [2021, None, None, None, None, None, None, None, None, ""],
        [2020, None, None, None, None, None, None, None, None, ""],
        [2026, None, None, None, None, None, None, None, None, "Fill when the 2026 annual report is out"],
    ])
for r in range(2, 14):
    s.cell(row=r, column=6, value=f'=IF(AND(ISNUMBER(B{r}),ISNUMBER(C{r}),C{r}>0),B{r}/C{r},"")')
    s.cell(row=r, column=6).font = N
    s.cell(row=r, column=6).fill = PatternFill(fill_type=None)
    s.cell(row=r, column=6).number_format = "0.00"
    for c in (2, 3):
        s.cell(row=r, column=c).number_format = "#,##0"
    s.cell(row=r, column=5).number_format = "0.00"
s["A2"].comment = Comment("2025 row is real data (Film Commission annual report via Argaam), so it doubles as the example.", "Template")

# ---------- annual_by_country ----------
s = sheet("annual_by_country",
    ["year", "country_of_production", "revenue_share_pct", "num_films", "revenue_sar", "source_url"],
    [2024, "USA", 0.585, 180, None, U3],
    rows=60, widths={"country_of_production": 22, "source_url": 45},
    comments={"revenue_share_pct": "As a fraction: 58.5% → 0.585",
              "revenue_sar": "If the report gives only %, leave blank. The notebook computes it from annual_summary."},
    extra=[
        [2024, "Egypt", 0.251, 45, None, U3],
        [2024, "Saudi Arabia", 0.078, 17, None, U3],
        [2024, "India", 0.0397, 109, None, U3],
    ])
for r in range(2, 62):
    s.cell(row=r, column=3).number_format = "0.0%"
    s.cell(row=r, column=5).number_format = "#,##0"
s.add_data_validation(dv2); dv2.add("B2:B61")

# ---------- annual_by_city ----------
s = sheet("annual_by_city",
    ["year", "city", "revenue_sar", "tickets_sold", "cinemas", "screens", "revenue_per_screen", "source_url"],
    [2024, "Riyadh", 391100000, 7400000, None, None, None,
     "https://www.arabnews.pk/node/2623596/business-economy"],
    rows=150, widths={"source_url": 45, "revenue_per_screen": 20})
for r in range(2, 152):
    s.cell(row=r, column=7, value=f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(F{r}),F{r}>0),C{r}/F{r},"")')
    s.cell(row=r, column=7).font = N
    s.cell(row=r, column=7).fill = PatternFill(fill_type=None)
    for c in (3, 4, 7):
        s.cell(row=r, column=c).number_format = "#,##0"

# ---------- calendar_events ----------
ramadan = [("2020-04-24", "2020-05-23"), ("2021-04-13", "2021-05-12"), ("2022-04-02", "2022-05-01"),
           ("2023-03-23", "2023-04-20"), ("2024-03-11", "2024-04-09"), ("2025-03-01", "2025-03-29"),
           ("2026-02-18", "2026-03-19")]
fitr = [("2020-05-24", "2020-05-27"), ("2021-05-13", "2021-05-16"), ("2022-05-02", "2022-05-05"),
        ("2023-04-21", "2023-04-24"), ("2024-04-10", "2024-04-13"), ("2025-03-30", "2025-04-02"),
        ("2026-03-20", "2026-03-23")]
adha = [("2020-07-31", "2020-08-03"), ("2021-07-20", "2021-07-23"), ("2022-07-09", "2022-07-12"),
        ("2023-06-28", "2023-07-01"), ("2024-06-16", "2024-06-19"), ("2025-06-06", "2025-06-09"),
        ("2026-05-27", "2026-05-30")]
ev = []
for a, b in ramadan: ev.append([a, b, "Ramadan", "religious", "approx, verify"])
for a, b in fitr: ev.append([a, b, "Eid al-Fitr", "holiday", "approx, verify"])
for a, b in adha: ev.append([a, b, "Eid al-Adha", "holiday", "approx, verify"])
ev.append(["2020-03-16", "2021-06-01", "COVID-19 closure / restrictions", "shock", "Fill exact reopening date and capacity rules"])
ev.sort(key=lambda x: x[0])
s = sheet("calendar_events",
    ["start_date", "end_date", "event_name", "event_type", "notes"],
    ev[0], rows=80, widths={"event_name": 30, "notes": 40}, extra=ev[1:])
s["A2"].comment = Comment("Pre-filled rows. Add: Riyadh Season, National Day, Founding Day, school holidays, Saudi Cinema Day, big releases.", "Template")

# ---------- Roadmap ----------
s = wb.create_sheet("Roadmap")
hdr = ["#", "Phase", "Task", "Deliverable", "Status", "Done?"]
for c, h in enumerate(hdr, 1):
    cell = s.cell(row=1, column=c, value=h)
    cell.font = Font(name=F, bold=True, color="FFFFFF"); cell.fill = HEAD; cell.border = BOX
tasks = [
    ("1. Collect", "Fill annual_summary for 2020–2025", "annual_summary tab complete"),
    ("1. Collect", "Fill annual_by_country (every year available)", "annual_by_country tab"),
    ("1. Collect", "Fill annual_by_city (every year available)", "annual_by_city tab"),
    ("1. Collect", "Collect weekly totals (start with 2024–2026, then go back)", "weekly_box_office tab"),
    ("1. Collect", "Collect weekly top films (top 5–10 per week)", "weekly_top_films tab"),
    ("1. Collect", "Verify calendar dates + add Riyadh Season etc.", "calendar_events tab"),
    ("2. Clean", "Run 01_load_and_validate.ipynb, fix every flagged row", "data/processed/*.csv + cinema.db"),
    ("3. Analyse (SQL)", "Headline: is the market flat since 2022?", "sql/analysis.sql section 0"),
    ("3. Analyse (SQL)", "Q1: Saudi films growing the pie or taking share?", "sql/analysis.sql section 1"),
    ("3. Analyse (SQL)", "Q2: Which cities are underserved?", "sql/analysis.sql section 2"),
    ("3. Analyse (SQL)", "Q3: Seasonality: when do peaks and dips happen?", "sql/analysis.sql section 3"),
    ("4. Visualise", "Python charts for the README", "reports/figures/*.png"),
    ("4. Visualise", "Power BI dashboard (3 pages: Content, Location, Timing)", "dashboard/*.pbix + screenshots"),
    ("5. Story", "Write findings + 3 recommendations + limitations", "README final version"),
    ("5. Story", "Publish to GitHub + add to ghadi.dev + LinkedIn post", "Live links"),
]
sv = DataValidation(type="list", formula1='"Not started,In progress,Done"', allow_blank=False)
s.add_data_validation(sv)
for i, (p, t, d) in enumerate(tasks, 2):
    vals = [i - 1, p, t, d, "Not started"]
    for c, v in enumerate(vals, 1):
        cell = s.cell(row=i, column=c, value=v); cell.font = N; cell.border = BOX
    s.cell(row=i, column=5).fill = INPUT
    sv.add(f"E{i}")
    s.cell(row=i, column=6, value=f'=IF(E{i}="Done",1,0)').font = N
    s.cell(row=i, column=6).border = BOX
last = len(tasks) + 1
s.cell(row=last + 2, column=3, value="Progress").font = Font(name=F, bold=True)
c = s.cell(row=last + 2, column=4, value=f"=SUM(F2:F{last})/COUNTA(C2:C{last})")
c.number_format = "0%"; c.font = Font(name=F, bold=True)
s.conditional_formatting.add(f"E2:E{last}", CellIsRule(operator="equal", formula=['"Done"'], fill=PatternFill("solid", fgColor="C6EFCE")))
s.conditional_formatting.add(f"E2:E{last}", CellIsRule(operator="equal", formula=['"In progress"'], fill=PatternFill("solid", fgColor="FFEB9C")))
for col, w in zip("ABCDEF", [5, 18, 55, 40, 14, 8]):
    s.column_dimensions[col].width = w
s.freeze_panes = "A2"

wb.save("data/raw/saudi_box_office_collection.xlsx")
print("ok")
