from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from src.benchmarking import top_drivers
from src.simulator import recommend_scenario


def generate_recommendations(row: pd.Series) -> List[str]:
    recs = []
    if row["attendance_pct"] >= 0.82 and row["ticket_price_proxy"] < 35:
        recs.append("Ticketing: test targeted price lifts on high-demand sections to close value gap.")
    else:
        recs.append("Ticketing: expand dynamic bundles to lift yield without suppressing demand.")

    if row["engagement_momentum"] < 0:
        recs.append("Marketing: invest in fan acquisition around key series to stabilize demand.")
    else:
        recs.append("Marketing: scale always-on content and CRM to convert momentum into renewals.")

    if row["sponsorship_proxy"] < 95:
        recs.append("Sponsorship: package digital inventory with local partner activations.")
    else:
        recs.append("Sponsorship: pursue premium category exclusives tied to broadcast reach.")
    return recs


def build_club_memo(row: pd.Series) -> str:
    drivers = top_drivers(row)
    params, sim = recommend_scenario(row)

    memo = f"# {row['team_name']} | Club Strategy Memo ({int(row['season'])})\n\n"
    memo += f"**Tier:** {row['cpi_tier']}  \n**CPI:** {row['cpi']:.1f}\n\n"
    memo += "## Key Drivers\n"
    memo += f"- {drivers[0]}\n- {drivers[1]}\n- {drivers[2]}\n\n"
    memo += "## Recommendations\n"
    for rec in generate_recommendations(row):
        memo += f"- {rec}\n"
    memo += "\n"
    memo += "## Expected Impact\n"
    memo += (
        f"- Scenario: price +{params['price_change_pct']*100:.0f}%, marketing +{params['marketing_lift_pct']*100:.0f}%, wins +{params['win_change_pct']*100:.0f}%\n"
        f"- Revenue proxy change: {sim.revenue_change_pct*100:.1f}%\n"
    )
    return memo


def build_league_memo(df: pd.DataFrame) -> str:
    latest_season = df["season"].max()
    latest = df[df["season"] == latest_season].copy()
    under_monetized = latest[(latest["attendance_pct"] > 0.8) & (latest["ticket_price_proxy"] < 34)]
    demand_constrained = latest[(latest["attendance_pct"] < 0.65) & (latest["ticket_price_proxy"] < 32)]

    memo = f"# League Opportunity Memo ({int(latest_season)})\n\n"
    memo += "## Top Opportunities\n"
    memo += f"- Under-monetized clubs: {', '.join(under_monetized['team_name'].head(5)) or 'None'}\n"
    memo += f"- Demand-constrained clubs: {', '.join(demand_constrained['team_name'].head(5)) or 'None'}\n\n"
    memo += "## CPI Leaders\n"
    leaders = latest.sort_values("cpi", ascending=False).head(5)
    for _, row in leaders.iterrows():
        memo += f"- {row['team_name']}: CPI {row['cpi']:.1f}\n"
    memo += "\n"
    memo += "## League Recommendations\n"
    memo += "- Align ticketing strategy with demand tiers; expand dynamic packaging for mid-tier clubs.\n"
    memo += "- Leverage playoff momentum to lock in sponsorship renewals before Q4.\n"
    memo += "- Invest in fan lifecycle analytics to improve retention in softer markets.\n"
    return memo


def write_memos(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    latest_season = df["season"].max()
    latest = df[df["season"] == latest_season]

    for _, row in latest.iterrows():
        memo = build_club_memo(row)
        (output_dir / f"{row['team_id']}.md").write_text(memo, encoding="utf-8")

    league_memo = build_league_memo(df)
    (output_dir / "league_memo.md").write_text(league_memo, encoding="utf-8")
