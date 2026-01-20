CREATE TABLE teams (
  team_id TEXT PRIMARY KEY,
  team_name TEXT,
  league TEXT,
  division TEXT
);

CREATE TABLE market_tiers (
  team_id TEXT,
  market_tier TEXT,
  metro_population_m REAL
);

CREATE TABLE attendance_by_team_year (
  team_id TEXT,
  season INTEGER,
  home_attendance INTEGER,
  wins INTEGER,
  playoff_flag INTEGER
);

CREATE TABLE club_metrics (
  team_id TEXT,
  season INTEGER,
  cpi REAL,
  cpi_tier TEXT,
  attendance_pct REAL,
  ticket_price_proxy REAL,
  revenue_proxy REAL,
  engagement_momentum REAL,
  operational_efficiency REAL
);
