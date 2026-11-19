-- Saudi Box Office: analysis queries
-- Business problem: box office has stayed around SR900M since 2022. What can grow it?
-- Run in DB Browser for SQLite, VS Code SQLite extension, or from notebook 02.
-- These are STARTER queries. Once your data is in, improve them and add your own.

-------------------------------------------------------------------
-- 0. HEADLINE: is the market flat?
-------------------------------------------------------------------
-- Year-over-year growth in revenue and tickets
SELECT
    year,
    total_revenue_sar / 1e6                                   AS revenue_m_sar,
    tickets_sold / 1e6                                        AS tickets_m,
    ROUND(total_revenue_sar * 1.0 / tickets_sold, 2)          AS avg_price,
    ROUND(100.0 * (total_revenue_sar - LAG(total_revenue_sar) OVER (ORDER BY year))
          / LAG(total_revenue_sar) OVER (ORDER BY year), 1)   AS revenue_yoy_pct,
    ROUND(1.0 * total_revenue_sar / screens / 1e6, 2)         AS revenue_per_screen_m
FROM annual_summary
ORDER BY year;
-- TODO: if screens keep growing but revenue doesn't → revenue per screen is falling.
--       That is a strong finding for operators.

-------------------------------------------------------------------
-- 1. CONTENT: are Saudi films growing the pie or taking share?
-------------------------------------------------------------------
-- 1a. Revenue by country of production per year (SAR)
SELECT
    c.year,
    c.country_of_production,
    ROUND(100 * c.revenue_share_pct, 1)                              AS share_pct,
    ROUND(COALESCE(c.revenue_sar, c.revenue_share_pct * s.total_revenue_sar) / 1e6, 1) AS revenue_m_sar,
    c.num_films,
    ROUND(COALESCE(c.revenue_sar, c.revenue_share_pct * s.total_revenue_sar) / c.num_films / 1e6, 2) AS revenue_per_film_m
FROM annual_by_country c
JOIN annual_summary s USING (year)
ORDER BY c.year, share_pct DESC;

-- 1b. Saudi vs everything else: did non-Saudi revenue shrink while Saudi grew?
SELECT
    c.year,
    SUM(CASE WHEN c.country_of_production = 'Saudi Arabia'
             THEN c.revenue_share_pct * s.total_revenue_sar END) / 1e6 AS saudi_m,
    (s.total_revenue_sar
     - SUM(CASE WHEN c.country_of_production = 'Saudi Arabia'
                THEN c.revenue_share_pct * s.total_revenue_sar END)) / 1e6 AS non_saudi_m
FROM annual_by_country c
JOIN annual_summary s USING (year)
GROUP BY c.year
ORDER BY c.year;
-- Interpretation: Saudi up and non-Saudi down by a similar amount → "taking share".
--                 Saudi up and non-Saudi flat → "growing the pie".

-- 1c. Weekly view: in weeks where a Saudi film is #1, is the total market bigger than usual?
SELECT
    CASE WHEN t.is_saudi = 'Y' THEN 'Saudi film #1' ELSE 'Foreign film #1' END AS top_film_type,
    COUNT(*)                                   AS weeks,
    ROUND(AVG(w.total_revenue_sar) / 1e6, 2)   AS avg_week_revenue_m,
    ROUND(AVG(w.tickets_sold))                 AS avg_week_tickets
FROM weekly_top_films t
JOIN weekly_box_office w USING (week_start)
WHERE t.rank = 1
GROUP BY top_film_type;
-- Caution: correlation ≠ causation (e.g. Saudi films often release on Eid, which is already a peak).
-- Fix idea: compare only Eid weeks with each other.

-------------------------------------------------------------------
-- 2. LOCATION: which cities are underserved?
-------------------------------------------------------------------
-- Revenue, tickets and screens per city. High revenue per screen = demand > supply.
SELECT
    year,
    city,
    ROUND(revenue_sar / 1e6, 1)                         AS revenue_m_sar,
    tickets_sold,
    screens,
    ROUND(revenue_sar / screens / 1e6, 2)               AS revenue_per_screen_m,
    ROUND(1.0 * tickets_sold / screens)                 AS tickets_per_screen,
    RANK() OVER (PARTITION BY year ORDER BY revenue_sar * 1.0 / screens DESC) AS demand_rank
FROM annual_by_city
WHERE screens > 0
ORDER BY year, demand_rank;
-- Extension: add population per city (GASTAT census) → screens per 100k people.

-------------------------------------------------------------------
-- 3. TIMING: when do peaks and dips happen?
-------------------------------------------------------------------
-- 3a. Monthly revenue across years (seasonality pattern)
SELECT
    strftime('%Y', week_start)                 AS year,
    strftime('%m', week_start)                 AS month,
    ROUND(SUM(total_revenue_sar) / 1e6, 1)     AS revenue_m_sar,
    SUM(tickets_sold)                          AS tickets
FROM weekly_box_office
GROUP BY year, month
ORDER BY year, month;

-- 3b. Tag every week with the event it overlaps (Ramadan, Eid, ...)
SELECT
    COALESCE(e.event_name, 'Normal week')      AS period,
    COUNT(*)                                   AS weeks,
    ROUND(AVG(w.total_revenue_sar) / 1e6, 2)   AS avg_week_revenue_m,
    ROUND(AVG(w.tickets_sold))                 AS avg_week_tickets
FROM weekly_box_office w
LEFT JOIN calendar_events e
       ON w.week_start <= e.end_date
      AND w.week_end   >= e.start_date
      AND e.event_type <> 'shock'
GROUP BY period
ORDER BY avg_week_revenue_m DESC;
-- Note: a week can overlap two events → it appears twice. Decide how to handle that and explain your choice.
