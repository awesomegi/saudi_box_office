-- Saudi Box Office: database schema (SQLite)
-- Created by notebooks/01_load_and_validate.ipynb → data/processed/cinema.db
-- One table per tab in data/raw/saudi_box_office_collection.xlsx

DROP TABLE IF EXISTS weekly_box_office;
CREATE TABLE weekly_box_office (
    week_start        DATE PRIMARY KEY,
    week_end          DATE NOT NULL,
    total_revenue_sar REAL,
    tickets_sold      INTEGER,
    films_screened    INTEGER,
    source_url        TEXT,
    notes             TEXT,
    CHECK (week_end >= week_start)
);

DROP TABLE IF EXISTS weekly_top_films;
CREATE TABLE weekly_top_films (
    week_start              DATE NOT NULL,
    rank                    INTEGER,
    film_title              TEXT NOT NULL,
    country_of_production   TEXT,
    is_saudi                TEXT CHECK (is_saudi IN ('Y','N')),
    age_rating              TEXT,
    weekly_revenue_sar      REAL,
    weekly_tickets          INTEGER,
    cumulative_revenue_sar  REAL,
    source_url              TEXT,
    PRIMARY KEY (week_start, film_title)
);

DROP TABLE IF EXISTS annual_summary;
CREATE TABLE annual_summary (
    year                 INTEGER PRIMARY KEY,
    total_revenue_sar    REAL,
    tickets_sold         INTEGER,
    films_screened       INTEGER,
    avg_ticket_price_sar REAL,
    cinemas              INTEGER,
    screens              INTEGER,
    cities               INTEGER,
    source_url           TEXT
);

DROP TABLE IF EXISTS annual_by_country;
CREATE TABLE annual_by_country (
    year                  INTEGER NOT NULL,
    country_of_production TEXT NOT NULL,
    revenue_share_pct     REAL,      -- fraction: 0.585 = 58.5%
    num_films             INTEGER,
    revenue_sar           REAL,      -- filled by notebook if blank
    source_url            TEXT,
    PRIMARY KEY (year, country_of_production)
);

DROP TABLE IF EXISTS annual_by_city;
CREATE TABLE annual_by_city (
    year          INTEGER NOT NULL,
    city          TEXT NOT NULL,
    revenue_sar   REAL,
    tickets_sold  INTEGER,
    cinemas       INTEGER,
    screens       INTEGER,
    source_url    TEXT,
    PRIMARY KEY (year, city)
);

DROP TABLE IF EXISTS calendar_events;
CREATE TABLE calendar_events (
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL,
    event_name  TEXT NOT NULL,
    event_type  TEXT,
    notes       TEXT
);
