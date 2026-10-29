"""Unit tests for end-to-end reconciliation and invariant integrity checks."""

import pytest
import duckdb
from src.metrics import MetricsEngine
from src.transformations import TransformationOrchestrator
from src.payment_attribution import AttributionEngine


def test_reconciliation_monetary_balance(populated_test_db):
    """Verifies that the deduplication balance equation balances to 0.00."""
    con = populated_test_db
    transform = TransformationOrchestrator(con=con)
    transform.run_clean_models()
    transform.run_golden_dataset()
    transform.run_features()

    attribution = AttributionEngine(con=con)
    attribution.run_attribution()

    metrics_engine = MetricsEngine(con=con)
    monetary_trail, dedup_balance, invariant_failures = metrics_engine.run_reconciliation()

    # Balance check: audit_discrepancy_inr must equal 0.0
    if not dedup_balance.empty:
        discrepancy = dedup_balance["audit_discrepancy_inr"].iloc[0]
        assert abs(discrepancy) < 0.0001, f"Audit discrepancy found: {discrepancy}"

    # Invariant failures must be empty
    assert len(invariant_failures) == 0, f"Invariant failures: {invariant_failures.to_dict('records')}"
