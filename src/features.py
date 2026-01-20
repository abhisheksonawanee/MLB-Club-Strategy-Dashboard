from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.utils import RAW_DIR


@dataclass
class PriceModelResult:
    model: LinearRegression
    coefficients: Dict[str, float]
    r2: float


def load_raw_data() -> Dict[str, pd.DataFrame]:
    teams = pd.read_csv(RAW_DIR / "teams_master.csv")
    market = pd.read_csv(RAW_DIR / "market_tiers.csv")
    attendance = pd.read_csv(RAW_DIR / "attendance_by_team_year.csv")
    capacity = pd.read_csv(RAW_DIR / "stadium_capacity.csv")
    attendance = maybe_update_with_pybaseball(attendance, teams)
    return {
        "teams": teams,
        "market": market,
        "attendance": attendance,
        "capacity": capacity,
    }


def add_market_features(df: pd.DataFrame) -> pd.DataFrame:
    tier_base = {"Large": 45, "Medium": 35, "Small": 28}
    tier_mult = {"Large": 1.15, "Medium": 1.0, "Small": 0.9}
    df = df.copy()
    df["market_base_price"] = df["market_tier"].map(tier_base).fillna(30)
    df["market_multiplier"] = df["market_tier"].map(tier_mult).fillna(1.0)
    return df


def compute_ticket_price_proxy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["wins_percentile"] = df.groupby("season")["wins"].rank(pct=True)
    df["ticket_price_proxy"] = (
        df["market_base_price"] * (0.9 + 0.3 * df["wins_percentile"])
    ).round(2)
    return df


def compute_sponsorship_proxy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["playoff_rate"] = (
        df.groupby("team_id")["playoff_flag"].rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["sponsorship_proxy"] = (
        100
        * df["market_multiplier"]
        * (1 + 0.2 * df["playoff_rate"] + 0.15 * df["wins_percentile"])
    ).round(1)
    return df


def compute_attendance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["attendance_pct"] = (df["home_attendance"] / (df["stadium_capacity"] * 81)).clip(0, 1)
    df["attendance_yoy_growth"] = (
        df.groupby("team_id")["home_attendance"].pct_change().fillna(0)
    )
    df["attendance_consistency"] = (
        1
        - df.groupby("team_id")["attendance_pct"].rolling(4, min_periods=2).std().reset_index(level=0, drop=True).fillna(0)
    )
    df["attendance_consistency"] = df["attendance_consistency"].clip(0, 1)
    return df


def compute_engagement_momentum(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rolling_wins = (
        df.groupby("team_id")["wins"].rolling(3, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["wins_trend"] = (df["wins"] - rolling_wins) / 20
    df["engagement_momentum"] = (df["wins_trend"] + 0.5 * df["playoff_rate"]).clip(-1, 1)
    return df


def build_price_sensitivity_model(df: pd.DataFrame) -> PriceModelResult:
    model_df = df[["attendance_pct", "ticket_price_proxy", "wins", "market_tier"]].dropna().copy()
    dummies = pd.get_dummies(model_df["market_tier"], prefix="tier", drop_first=True)
    x = pd.concat([model_df[["ticket_price_proxy", "wins"]], dummies], axis=1)
    y = model_df["attendance_pct"]
    model = LinearRegression()
    model.fit(x, y)
    r2 = model.score(x, y)
    coefficients = {"ticket_price_proxy": model.coef_[0], "wins": model.coef_[1]}
    for i, col in enumerate(dummies.columns, start=2):
        coefficients[col] = model.coef_[i]
    return PriceModelResult(model=model, coefficients=coefficients, r2=r2)


def maybe_update_with_pybaseball(
    attendance: pd.DataFrame, teams: pd.DataFrame
) -> pd.DataFrame:
    """Optionally update wins/playoff flags via pybaseball standings."""
    import os
    import logging

    logger = logging.getLogger(__name__)
    if os.getenv("USE_PYBASEBALL", "0") != "1":
        return attendance

    try:
        from pybaseball import standings  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.warning("pybaseball unavailable: %s", exc)
        return attendance

    years = sorted(attendance["season"].unique())
    frames = []
    for year in years:
        try:
            result = standings(year)
        except Exception as exc:  # pragma: no cover - optional dependency path
            logger.warning("pybaseball standings failed for %s: %s", year, exc)
            return attendance

        dfs = []
        if isinstance(result, pd.DataFrame):
            dfs = [result]
        elif isinstance(result, (list, tuple)):
            for item in result:
                if isinstance(item, pd.DataFrame):
                    dfs.append(item)
                elif isinstance(item, list):
                    dfs.extend([df for df in item if isinstance(df, pd.DataFrame)])

        for df in dfs:
            team_col = next((c for c in df.columns if c.lower() in {"tm", "team", "club"}), None)
            wins_col = next((c for c in df.columns if c.lower() in {"w", "wins"}), None)
            if not team_col or not wins_col:
                continue
            temp = df[[team_col, wins_col]].copy()
            temp.columns = ["team_name", "wins"]
            temp["season"] = year
            frames.append(temp)

    if not frames:
        logger.warning("pybaseball returned no usable standings; using raw data")
        return attendance

    standings_df = pd.concat(frames, ignore_index=True)
    standings_df["team_name_norm"] = (
        standings_df["team_name"].astype(str).str.replace("*", "", regex=False).str.lower()
    )
    teams_map = teams[["team_id", "team_name"]].copy()
    teams_map["team_name_norm"] = teams_map["team_name"].str.lower()
    standings_df = standings_df.merge(teams_map, on="team_name_norm", how="left")
    standings_df = standings_df.dropna(subset=["team_id"])
    standings_df = standings_df[["team_id", "season", "wins"]]

    updated = attendance.merge(standings_df, on=["team_id", "season"], how="left", suffixes=("", "_pyb"))
    updated["wins"] = updated["wins_pyb"].fillna(updated["wins"]).astype(int)
    updated["playoff_flag"] = (updated["wins"] >= 88).astype(int)
    updated = updated.drop(columns=["wins_pyb"])
    logger.info("pybaseball wins updates applied")
    return updated
