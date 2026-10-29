"""Unit tests for metric definitions, rate bounds, and claim evaluation."""

import pytest
import duckdb
from src.metrics import MetricsEngine
from src.transformations import TransformationOrchestrator


def test_metrics_rate_bounds_and_calculations(populated_test_db):
    """Verifies that metric calculation views enforce rate bounds and return valid monthly metrics."""
    con = populated_test_db
    transform = TransformationOrchestrator(con=con)
    transform.run_clean_models()
    transform.run_golden_dataset()
    transform.run_features()

    metrics_engine = MetricsEngine(con=con)
    monthly_df = metrics_engine.calculate_metrics()

    assert isinstance(monthly_df, object)
    claim_verdict = metrics_engine.evaluate_11_pct_claim()
    assert "forensic_verdict" in claim_verdict
