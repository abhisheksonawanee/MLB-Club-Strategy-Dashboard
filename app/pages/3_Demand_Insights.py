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

from components.charts import scatter_chart
from src.features import build_price_sensitivity_model
from src.utils import PROCESSED_DIR

st.set_page_config(page_title="Demand Insights", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "club_metrics.csv")


def main() -> None:
    st.title("Demand Insights")
    df = load_data()

    latest = df[df["season"] == df["season"].max()]
    st.plotly_chart(
        scatter_chart(latest, "ticket_price_proxy", "attendance_pct", "market_tier", "team_name", "Demand vs Price Proxy"),
        use_container_width=True,
    )

    model = build_price_sensitivity_model(df)
    st.subheader("Price Sensitivity Proxy")
    st.write(f"R2: {model.r2:.2f}")
    st.write(pd.DataFrame([model.coefficients]))

    under = latest[(latest["attendance_pct"] > 0.8) & (latest["ticket_price_proxy"] < 34)]
    constrained = latest[(latest["attendance_pct"] < 0.65) & (latest["ticket_price_proxy"] < 32)]

    st.subheader("Under-monetized Clubs")
    st.dataframe(under[["team_name", "attendance_pct", "ticket_price_proxy"]].sort_values("attendance_pct", ascending=False))

    st.subheader("Demand-constrained Clubs")
    st.dataframe(constrained[["team_name", "attendance_pct", "ticket_price_proxy"]].sort_values("attendance_pct"))


if __name__ == "__main__":
    main()
