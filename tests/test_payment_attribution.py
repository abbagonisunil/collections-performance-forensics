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


def test_multiple_calls_matching_single_payment_anti_fanout():
    """Explicitly tests that when an account has 5 calls within the lookback window,
    a single payment is attributed deterministically to exactly ONE primary call
    and opening exposure / payment cash is not multiplied.
    """
    con = duckdb.connect(":memory:")
    # Create required tables
    con.execute("""
        CREATE TABLE fact_payment (
            payment_id VARCHAR PRIMARY KEY,
            account_id VARCHAR,
            amount_paid DOUBLE,
            payment_timestamp TIMESTAMP
        );
        CREATE TABLE fact_interaction (
            interaction_id VARCHAR PRIMARY KEY,
            account_id VARCHAR,
            agent_id VARCHAR,
            campaign_id VARCHAR,
            channel VARCHAR,
            interaction_timestamp TIMESTAMP,
            is_rpc BOOLEAN
        );
    """)

    # 1 payment of ₹10,000 on 2024-05-15
    con.execute("""
        INSERT INTO fact_payment VALUES 
        ('PAY_001', 'ACC_100', 10000.0, '2024-05-15 14:00:00');
    """)

    # 5 prior calls within 14 days by different agents
    con.execute("""
        INSERT INTO fact_interaction VALUES
        ('CALL_1', 'ACC_100', 'AGENT_A', 'CAMP_1', 'CALL', '2024-05-02 10:00:00', FALSE),
        ('CALL_2', 'ACC_100', 'AGENT_B', 'CAMP_1', 'CALL', '2024-05-05 11:00:00', FALSE),
        ('CALL_3', 'ACC_100', 'AGENT_C', 'CAMP_1', 'CALL', '2024-05-08 12:00:00', FALSE),
        ('CALL_4', 'ACC_100', 'AGENT_D', 'CAMP_2', 'CALL', '2024-05-11 15:00:00', TRUE),
        ('CALL_5', 'ACC_100', 'AGENT_E', 'CAMP_2', 'CALL', '2024-05-14 16:00:00', TRUE);
    """)

    engine = AttributionEngine(con=con)
    engine.run_attribution(window_days=14)

    # Invariant 1: Exactly 1 primary interaction has last_touch_rank = 1
    primary_touches = con.execute("""
        SELECT COUNT(*) FROM bridge_payment_interaction 
        WHERE payment_id = 'PAY_001' AND last_touch_rank = 1;
    """).fetchone()[0]
    assert primary_touches == 1, "Payment must have exactly one primary last-touch attribution"

    # Invariant 2: The primary interaction is the most recent (CALL_5)
    last_touch_id = con.execute("""
        SELECT interaction_id FROM bridge_payment_interaction 
        WHERE payment_id = 'PAY_001' AND last_touch_rank = 1;
    """).fetchone()[0]
    assert last_touch_id == "CALL_5", "Deterministic tie-breaker must select the latest interaction"

    # Invariant 3: Total attributed cash across all interactions equals canonical cash (₹10,000), not ₹50,000
    total_attributed = con.execute("""
        SELECT SUM(amount_paid * weight_last_touch) 
        FROM bridge_payment_interaction 
        WHERE payment_id = 'PAY_001';
    """).fetchone()[0]
    assert total_attributed == 10000.0, "Attribution must not multiply payment amount across matching calls"
