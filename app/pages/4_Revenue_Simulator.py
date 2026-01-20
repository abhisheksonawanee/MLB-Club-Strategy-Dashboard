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

from components.charts import waterfall_chart
from src.simulator import recommend_scenario, simulate_scenario
from src.utils import PROCESSED_DIR

st.set_page_config(page_title="Revenue Simulator", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "club_metrics.csv")


def main() -> None:
    st.title("Revenue Opportunity Simulator")
    df = load_data()

    latest = df[df["season"] == df["season"].max()]
    club = st.sidebar.selectbox("Club", latest["team_name"].sort_values())

    row = latest[latest["team_name"] == club].iloc[0]

    price_change = st.sidebar.slider("Ticket price change %", -10, 15, 3) / 100
    marketing_lift = st.sidebar.slider("Marketing lift %", 0, 20, 5) / 100
    win_change = st.sidebar.slider("Win% change", -5, 10, 2) / 100
    market_condition = st.sidebar.selectbox("Market conditions", ["Strong", "Neutral", "Soft"])

    result = simulate_scenario(row, price_change, marketing_lift, win_change, market_condition)

    col1, col2, col3 = st.columns(3)
    col1.metric("Projected attendance", f"{result.projected_attendance:,.0f}", f"{result.attendance_change_pct*100:.1f}%")
    col2.metric("Projected revenue proxy", f"${result.projected_revenue/1_000_000:.1f}M", f"{result.revenue_change_pct*100:.1f}%")
    col3.metric("Confidence band", f"${result.confidence_low/1_000_000:.1f}M - ${result.confidence_high/1_000_000:.1f}M")

    base_revenue = row["home_attendance"] * row["ticket_price_proxy"]
    change = result.projected_revenue - base_revenue
    st.plotly_chart(waterfall_chart(base_revenue, change, "Revenue Proxy Impact"), use_container_width=True)

    st.subheader("Recommended Scenario (Risk-Adjusted)")
    params, rec = recommend_scenario(row)
    st.write(
        f"Price +{params['price_change_pct']*100:.0f}%, "
        f"Marketing +{params['marketing_lift_pct']*100:.0f}%, "
        f"Wins +{params['win_change_pct']*100:.0f}%"
    )
    st.write(f"Projected revenue change: {rec.revenue_change_pct*100:.1f}%")


if __name__ == "__main__":
    main()
