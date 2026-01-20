import pandas as pd

from src.simulator import simulate_scenario


def test_price_increase_raises_revenue():
    row = pd.Series({
        "home_attendance": 2_000_000,
        "ticket_price_proxy": 35.0,
    })
    base = simulate_scenario(row, 0.0, 0.0, 0.0, "Neutral")
    higher = simulate_scenario(row, 0.05, 0.0, 0.0, "Neutral")
    assert higher.projected_revenue > base.projected_revenue
