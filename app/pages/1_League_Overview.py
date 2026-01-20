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

from components.charts import line_chart, scatter_chart
from src.utils import PROCESSED_DIR

st.set_page_config(page_title="League Overview", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "club_metrics.csv")


def main() -> None:
    st.title("League Overview")
    df = load_data()

    season_range = st.sidebar.slider(
        "Season Range", int(df["season"].min()), int(df["season"].max()), (2018, int(df["season"].max()))
    )
    filtered = df[(df["season"] >= season_range[0]) & (df["season"] <= season_range[1])]

    trend = filtered.groupby("season")["home_attendance"].sum().reset_index()
    st.plotly_chart(line_chart(trend, "season", "home_attendance", title="League Attendance Trend"), use_container_width=True)

    latest = filtered[filtered["season"] == filtered["season"].max()]
    st.plotly_chart(
        scatter_chart(latest, "ticket_price_proxy", "attendance_pct", "market_tier", "team_name", "Demand vs Price Proxy"),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
