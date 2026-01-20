# MLB Club Strategy Dashboard

Executive-ready analytics dashboard aligned to the MLB Club Business Operations & Strategy role. The project benchmarks all 30 clubs, analyzes market and fan demand, and simulates revenue opportunities with actionable strategy memos.

## Why this matches MLB CBOS responsibilities
- **Benchmarking**: CPI scoring across fan development, revenue proxies, and operational excellence.
- **Cross-functional insight**: ticketing, marketing, sponsorship, finance perspectives embedded in metrics.
- **Executive communication**: auto-generated one-page club memos plus league opportunity memo.
- **Analytics to action**: simulator converts scenarios into revenue proxy impact with confidence bands.

## Data sources and assumptions
- Standings and team performance are modeled with public proxies and can be swapped with `pybaseball` in future iterations.
- Attendance proxy uses synthetic attendance derived from stadium capacity, wins, and market tier.
- Ticket price proxy is built from market tier base price and performance percentile.
- Market tier and metro population estimates are approximate public sources.
- Sponsorship proxy blends market size and TV exposure proxy (wins + playoff rates).

## Quickstart
```bash
pip install -r requirements.txt
python -m src.pipeline
streamlit run app/app.py
```

Optional live standings refresh:
```bash
set USE_PYBASEBALL=1
python -m src.pipeline
```

## Repository structure
- `app/`: Streamlit app and UI components
- `src/`: data pipeline, benchmarking, simulator, memo generator
- `data/raw`: offline CSV fallbacks for all 30 teams (2015-2024)
- `outputs/`: figures and memos

## Screenshots
- `outputs/figures/league_attendance_trend.png`
- `outputs/figures/demand_vs_price.png`

## Resume bullets
- Built an MLB-wide club benchmarking system (CPI) with demand, revenue, and operational efficiency proxies across 30 teams.
- Developed a revenue opportunity simulator translating pricing, marketing, and performance shifts into executive-ready impact ranges.
- Automated club strategy memos with top drivers and recommendations across ticketing, marketing, and sponsorship.
