from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src import benchmarking
from src.features import (
    add_market_features,
    build_price_sensitivity_model,
    compute_attendance_metrics,
    compute_engagement_momentum,
    compute_sponsorship_proxy,
    compute_ticket_price_proxy,
    load_raw_data,
)
from src.memos import write_memos
from src.utils import FIGURES_DIR, MEMOS_DIR, PROCESSED_DIR, ensure_dirs, setup_logging

logger = logging.getLogger(__name__)


def build_dataset() -> pd.DataFrame:
    """Build the club metrics dataset from raw inputs and feature engineering."""
    raw = load_raw_data()
    df = raw["attendance"].merge(raw["teams"], on="team_id", how="left")
    df = df.merge(raw["market"], on="team_id", how="left")
    df = df.merge(raw["capacity"], on="team_id", how="left")

    df = add_market_features(df)
    df = compute_ticket_price_proxy(df)
    df = compute_sponsorship_proxy(df)
    df = compute_attendance_metrics(df)
    df = compute_engagement_momentum(df)

    df["revenue_potential"] = (
        df["ticket_price_proxy"] * df["home_attendance"] * df["market_multiplier"]
    )
    df["revenue_proxy"] = df["revenue_potential"]

    df["fan_demand"] = (
        0.5 * df["attendance_pct"] + 0.25 * df["attendance_yoy_growth"] + 0.25 * df["attendance_consistency"]
    )

    df["operational_efficiency"] = df["attendance_consistency"]

    df = benchmarking.compute_cpi(df)
    df = benchmarking.assign_tiers(df)

    return df


def save_figures(df: pd.DataFrame, figures_dir: Path) -> None:
    """Create and save core figures used in the README and app."""
    figures_dir.mkdir(parents=True, exist_ok=True)

    attendance_trend = df.groupby("season")["home_attendance"].sum().reset_index()
    plt.figure(figsize=(8, 4))
    plt.plot(attendance_trend["season"], attendance_trend["home_attendance"] / 1_000_000)
    plt.title("League Attendance Trend")
    plt.xlabel("Season")
    plt.ylabel("Attendance (M)")
    plt.tight_layout()
    plt.savefig(figures_dir / "league_attendance_trend.png", dpi=150)
    plt.close()

    latest = df[df["season"] == df["season"].max()]
    plt.figure(figsize=(6, 4))
    plt.scatter(latest["ticket_price_proxy"], latest["attendance_pct"], alpha=0.8)
    plt.title("Demand vs Price Proxy")
    plt.xlabel("Ticket Price Proxy")
    plt.ylabel("Attendance %")
    plt.tight_layout()
    plt.savefig(figures_dir / "demand_vs_price.png", dpi=150)
    plt.close()


def main() -> None:
    """Run end-to-end pipeline: process data, save figures, write memos."""
    setup_logging()
    ensure_dirs([PROCESSED_DIR, FIGURES_DIR, MEMOS_DIR])

    df = build_dataset()
    df.to_csv(PROCESSED_DIR / "club_metrics.csv", index=False)

    model = build_price_sensitivity_model(df)
    coeffs = pd.DataFrame([model.coefficients])
    coeffs["r2"] = model.r2
    coeffs.to_csv(PROCESSED_DIR / "price_sensitivity_coeffs.csv", index=False)

    save_figures(df, FIGURES_DIR)
    write_memos(df, MEMOS_DIR)
    logger.info("Pipeline completed: processed data, figures, memos")


if __name__ == "__main__":
    main()
