"""Unit tests for omnichannel payment attribution and anti-fanout invariants."""

import pytest
import duckdb
from src.payment_attribution import AttributionEngine
from src.transformations import TransformationOrchestrator


def test_payment_attribution_anti_fanout(populated_test_db):
    """Verifies that payment attribution never multiplies or exceeds canonical collections."""
    con = populated_test_db
    transform = TransformationOrchestrator(con=con)
    transform.run_clean_models()
    transform.run_golden_dataset()

    engine = AttributionEngine(con=con)
    comp_df = engine.run_attribution(window_days=14)

    # Check total attributed in last touch
    total_canonical = con.execute("SELECT SUM(amount_paid) FROM clean_payments;").fetchone()[0] or 0.0

    # Total attributed across all channels in fact_payment_attribution
    total_attributed_last_touch = con.execute("SELECT SUM(attributed_inr_last_touch) FROM fact_payment_attribution;").fetchone()[0] or 0.0

    # Invariant: Attributed cash must never exceed canonical cash
    assert round(total_attributed_last_touch, 2) <= round(total_canonical, 2)
