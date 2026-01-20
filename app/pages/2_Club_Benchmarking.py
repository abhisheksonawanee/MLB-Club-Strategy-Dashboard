from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
for path in (ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from components.charts import bar_chart
from src.utils import PROCESSED_DIR

st.set_page_config(page_title="Club Benchmarking", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "club_metrics.csv")


def main() -> None:
    st.title("Club Benchmarking")
    df = load_data()

    season = st.sidebar.selectbox("Season", sorted(df["season"].unique()), index=len(df["season"].unique()) - 1)
    market_filter = st.sidebar.multiselect("Market Tier", sorted(df["market_tier"].unique()), default=sorted(df["market_tier"].unique()))

    filtered = df[(df["season"] == season) & (df["market_tier"].isin(market_filter))]
    ranking = filtered.sort_values("cpi", ascending=False)

    st.dataframe(
        ranking[["team_name", "market_tier", "cpi", "cpi_tier", "fan_demand_score", "revenue_potential_score"]]
        .style
        .background_gradient(subset=["cpi"], cmap="Blues")
        .format({"cpi": "{:.1f}", "fan_demand_score": "{:.1f}", "revenue_potential_score": "{:.1f}"}),
        use_container_width=True,
    )

    top10 = ranking.head(10)
    st.plotly_chart(bar_chart(top10, "team_name", "cpi", title="Top 10 CPI Clubs"), use_container_width=True)


if __name__ == "__main__":
    main()
