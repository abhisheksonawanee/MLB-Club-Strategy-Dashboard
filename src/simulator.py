from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd


@dataclass
class SimulationResult:
    projected_attendance: float
    projected_revenue: float
    attendance_change_pct: float
    revenue_change_pct: float
    confidence_low: float
    confidence_high: float


def simulate_scenario(
    row: pd.Series,
    price_change_pct: float,
    marketing_lift_pct: float,
    win_change_pct: float,
    market_condition: str = "Neutral",
) -> SimulationResult:
    base_attendance = row["home_attendance"]
    base_price = row["ticket_price_proxy"]

    price_elasticity = -0.35
    marketing_elasticity = 0.18
    win_elasticity = 0.25

    market_adjust = {"Strong": 1.1, "Neutral": 1.0, "Soft": 0.9}.get(market_condition, 1.0)

    attendance_change_pct = (
        price_elasticity * price_change_pct
        + marketing_elasticity * marketing_lift_pct
        + win_elasticity * win_change_pct
    ) * market_adjust

    attendance_change_pct = float(np.clip(attendance_change_pct, -0.25, 0.30))
    projected_attendance = base_attendance * (1 + attendance_change_pct)
    projected_price = base_price * (1 + price_change_pct)

    projected_revenue = projected_attendance * projected_price
    base_revenue = base_attendance * base_price
    revenue_change_pct = (projected_revenue - base_revenue) / base_revenue

    confidence_band = 0.08 + 0.1 * abs(price_change_pct)
    confidence_low = projected_revenue * (1 - confidence_band)
    confidence_high = projected_revenue * (1 + confidence_band)

    return SimulationResult(
        projected_attendance=projected_attendance,
        projected_revenue=projected_revenue,
        attendance_change_pct=attendance_change_pct,
        revenue_change_pct=revenue_change_pct,
        confidence_low=confidence_low,
        confidence_high=confidence_high,
    )


def recommend_scenario(row: pd.Series) -> Tuple[Dict[str, float], SimulationResult]:
    scenarios = []
    for price in [0.0, 0.03, 0.05, 0.07]:
        for marketing in [0.0, 0.05, 0.10]:
            for win in [0.0, 0.02, 0.04]:
                result = simulate_scenario(row, price, marketing, win, "Neutral")
                risk_adjusted = result.projected_revenue / (1 + 0.5 * abs(price))
                scenarios.append((risk_adjusted, price, marketing, win, result))
    best = max(scenarios, key=lambda x: x[0])
    params = {"price_change_pct": best[1], "marketing_lift_pct": best[2], "win_change_pct": best[3]}
    return params, best[4]
