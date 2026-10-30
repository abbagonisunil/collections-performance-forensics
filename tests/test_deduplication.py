"""Unit tests for payment deduplication and overstatement detection."""

import pytest
import duckdb
from src.deduplication import DeduplicationEngine


def test_deduplication_decisions_on_synthetic_fixtures(populated_test_db):
    """Verifies that exact duplicates, 3-min replay retries, and failed transactions are classified correctly."""
    con = populated_test_db
    dedup = DeduplicationEngine(con=con)
    audit_df = dedup.run_deduplication()

    # Query individual decisions from payment_deduplication_log
    decisions = dict(con.execute("SELECT payment_id, dedup_decision FROM payment_deduplication_log;").fetchall())

    # Assert individual classifications based on synthetic fixture specifications
    assert decisions["PAY_001"] == "RETAINED_CANONICAL"
    assert decisions["PAY_002"] == "EXCLUDED_EXACT_DUPLICATE"
    assert decisions["PAY_003"] == "RETAINED_CANONICAL"
    assert decisions["PAY_004"] == "FLAGGED_UNRESOLVED"
    assert decisions["PAY_005"] == "EXCLUDED_FAILED"
    assert decisions["PAY_006"] == "RETAINED_CANONICAL"
    assert decisions["PAY_007"] == "RETAINED_CANONICAL"


def test_recovery_inflation_calculation(populated_test_db):
    """Verifies that inflation impact correctly identifies difference between naive and canonical collections."""
    con = populated_test_db
    dedup = DeduplicationEngine(con=con)
    inflation = dedup.get_inflation_impact()

    # Total synthetic payments: 5k + 5k + 3k + 3k + 12k + 12k + 5k = 45,000 INR
    assert inflation["naive_gross_collections_inr"] == 45000.0

    # Canonical retained: PAY_001 (5k) + PAY_003 (3k) + PAY_006 (12k) + PAY_007 (5k) = 25,000 INR
    assert inflation["canonical_collections_inr"] == 25000.0

    # Overstatement: 45k - 25k = 20,000 INR (80.0% inflation over canonical cash)
    assert inflation["total_overstatement_inr"] == 20000.0
    assert inflation["recovery_inflation_pct"] == 80.0
