"""Normalize risk metrics from API/DB (stored as 0–100 percentage)."""


def risk_metric_pct(raw) -> float:
    """If legacy double-scaling left values > 100, divide once."""
    x = float(raw or 0)
    return x / 100 if x > 100 else x
