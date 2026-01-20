import pandas as pd

from src.benchmarking import compute_cpi


def test_cpi_range():
    df = pd.DataFrame({
        "season": [2024, 2024, 2024],
        "fan_demand": [0.5, 0.7, 0.9],
        "revenue_potential": [1.0, 2.0, 3.0],
        "engagement_momentum": [0.1, 0.2, 0.3],
        "operational_efficiency": [0.8, 0.6, 0.9],
    })
    scored = compute_cpi(df)
    assert scored["cpi"].between(0, 100).all()
