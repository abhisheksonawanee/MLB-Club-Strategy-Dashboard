from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
for path in (ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from components.kpi_cards import kpi_card
from components.styling import apply_base_styles
from src.pipeline import main as run_pipeline
from src.utils import PROCESSED_DIR

st.set_page_config(page_title="MLB Club Strategy Dashboard", layout="wide")
apply_base_styles()

@st.cache_data
def load_data() -> pd.DataFrame:
    metrics_path = PROCESSED_DIR / "club_metrics.csv"
    if not metrics_path.exists():
        run_pipeline()
    return pd.read_csv(metrics_path)


def main() -> None:
    st.title("MLB Club Strategy Dashboard")
    st.caption("League-wide club benchmarking, demand insights, and revenue simulation")

    df = load_data()
    latest_season = int(df["season"].max())
    latest = df[df["season"] == latest_season]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("League CPI Avg", f"{latest['cpi'].mean():.1f}")
    with col2:
        kpi_card("Top Club", latest.sort_values("cpi", ascending=False).iloc[0]["team_name"])
    with col3:
        kpi_card("Attendance Avg", f"{latest['attendance_pct'].mean()*100:.1f}%")
    revenue_col = "revenue_proxy" if "revenue_proxy" in latest.columns else "revenue_potential"
    with col4:
        kpi_card("Revenue Proxy Avg", f"${latest[revenue_col].mean()/1_000_000:.1f}M")

    st.markdown("Use the pages in the left sidebar to explore benchmarking, demand insights, and club memos.")


if __name__ == "__main__":
    main()
