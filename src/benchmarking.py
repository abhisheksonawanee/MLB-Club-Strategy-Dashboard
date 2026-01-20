from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

WEIGHTS: Dict[str, float] = {
    "fan_demand": 0.35,
    "revenue_potential": 0.30,
    "engagement_momentum": 0.20,
    "operational_efficiency": 0.15,
}


def normalize_by_season(df: pd.DataFrame, column: str) -> pd.Series:
    """Normalize a metric to percentile scores within each season."""
    return df.groupby("season")[column].rank(pct=True) * 100


def compute_component_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute CPI component scores as 0-100 percentiles."""
    df = df.copy()
    df["fan_demand_score"] = normalize_by_season(df, "fan_demand")
    df["revenue_potential_score"] = normalize_by_season(df, "revenue_potential")
    df["engagement_momentum_score"] = normalize_by_season(df, "engagement_momentum")
    df["operational_efficiency_score"] = normalize_by_season(df, "operational_efficiency")
    return df


def compute_cpi(df: pd.DataFrame, weights: Dict[str, float] | None = None) -> pd.DataFrame:
    """Compute Club Performance Index (CPI) using weighted components."""
    weights = weights or WEIGHTS
    df = compute_component_scores(df)
    df["cpi"] = (
        df["fan_demand_score"] * weights["fan_demand"]
        + df["revenue_potential_score"] * weights["revenue_potential"]
        + df["engagement_momentum_score"] * weights["engagement_momentum"]
        + df["operational_efficiency_score"] * weights["operational_efficiency"]
    )
    df["cpi"] = df["cpi"].round(2)
    return df


def assign_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Assign Top 5, Middle 20, Bottom 5 tiers based on CPI rank."""
    df = df.copy()
    df["cpi_rank"] = df.groupby("season")["cpi"].rank(ascending=False, method="first")
    df["cpi_tier"] = "Middle 20"
    df.loc[df["cpi_rank"] <= 5, "cpi_tier"] = "Top 5"
    df.loc[df["cpi_rank"] > 25, "cpi_tier"] = "Bottom 5"
    return df


def top_drivers(row: pd.Series) -> Tuple[str, str, str]:
    """Return the top three CPI component drivers for a club."""
    drivers = {
        "Fan Demand": row["fan_demand_score"],
        "Revenue Potential": row["revenue_potential_score"],
        "Engagement Momentum": row["engagement_momentum_score"],
        "Operational Efficiency": row["operational_efficiency_score"],
    }
    sorted_drivers = sorted(drivers.items(), key=lambda x: x[1], reverse=True)
    return tuple([d[0] for d in sorted_drivers[:3]])
