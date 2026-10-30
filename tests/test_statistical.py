"""Unit tests for statistical analysis and Kitagawa shift-share mix decomposition."""

import pytest
import numpy as np
import duckdb
from src.statistical_analysis import StatisticalInvestigator


def test_kitagawa_mix_decomposition_on_unpopulated_db():
    """Verifies that an unpopulated database returns an explicit AWAITING_REAL_DATA status
    without hardcoding fictional company numbers.
    """
    con = duckdb.connect(":memory:")
    investigator = StatisticalInvestigator(con=con)
    res = investigator.calculate_mix_decomposition()

    assert res["status"] == "AWAITING_REAL_DATA"
    assert res["total_change_pp"] is None
    assert res["within_operational_effect_pp"] is None
    assert res["between_mix_shift_effect_pp"] is None
    assert res["identity_verified"] is None


def test_kitagawa_decomposition_mathematical_solver():
    """Mathematically verifies that Kitagawa decomposition holds as an exact identity:
    Total Rate Change = Within-Segment Operational Effect + Between-Segment Mix Effect.
    """
    # 4 distinct segments (e.g. DPD 1-30, 31-60, 61-90, 90+)
    w0 = np.array([0.25, 0.30, 0.25, 0.20])
    w1 = np.array([0.45, 0.25, 0.18, 0.12])  # Volume shifted toward early bucket
    r0 = np.array([0.20, 0.10, 0.05, 0.02])
    r1 = np.array([0.218, 0.111, 0.057, 0.022])

    res = StatisticalInvestigator.decompose_kitagawa(r0, r1, w0, w1)

    total_change = res["total_change_pp"]
    within_effect = res["within_operational_effect_pp"]
    between_effect = res["between_mix_shift_effect_pp"]

    # Invariant: unrounded identity must hold exactly, rounded outputs within rounding tolerance
    assert res["identity_verified"] is True
    assert abs((within_effect + between_effect) - total_change) <= 0.002
    assert between_effect > 0, "Shift to high-recovery bucket must produce positive mix effect"


def test_arbitrary_kitagawa_identity_randomized():
    """Tests the mathematical identity of Kitagawa decomposition on arbitrary random weights and rates."""
    np.random.seed(42)
    for _ in range(25):
        k = np.random.randint(3, 10)  # Random segment count
        w0 = np.random.dirichlet(np.ones(k))
        w1 = np.random.dirichlet(np.ones(k))
        r0 = np.random.uniform(0.01, 0.50, k)
        r1 = np.random.uniform(0.01, 0.50, k)

        res = StatisticalInvestigator.decompose_kitagawa(r0, r1, w0, w1)

        total_change = res["total_change_pp"]
        within_effect = res["within_operational_effect_pp"]
        between_effect = res["between_mix_shift_effect_pp"]

        # Exact unrounded identity verified by solver
        assert res["identity_verified"] is True
        # Rounded outputs match within rounding tolerance
        assert abs((within_effect + between_effect) - total_change) <= 0.002


def test_multiple_payments_per_account_no_exposure_fanout():
    """Explicitly verifies that when an account has multiple payment records,
    opening principal is NOT multiplied / fanned out in statistical queries.
    """
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE dim_account (
            account_id VARCHAR PRIMARY KEY,
            dpd_bucket VARCHAR,
            due_date DATE,
            opening_principal DOUBLE
        );
        CREATE TABLE clean_payments (
            payment_id VARCHAR PRIMARY KEY,
            account_id VARCHAR,
            amount_paid DOUBLE
        );
    """)

    # 1 account with ₹50,000 opening exposure in PRE period
    con.execute("""
        INSERT INTO dim_account VALUES 
        ('ACC_1', 'DPD_31_60', '2024-03-15', 50000.0);
    """)

    # 4 distinct payment installments of ₹5,000 each (Total ₹20,000)
    con.execute("""
        INSERT INTO clean_payments VALUES 
        ('PAY_1', 'ACC_1', 5000.0),
        ('PAY_2', 'ACC_1', 5000.0),
        ('PAY_3', 'ACC_1', 5000.0),
        ('PAY_4', 'ACC_1', 5000.0);
    """)

    # Also add 1 account in POST period so Simpson's query can evaluate multi-period
    con.execute("""
        INSERT INTO dim_account VALUES 
        ('ACC_2', 'DPD_31_60', '2024-08-15', 60000.0);
        INSERT INTO clean_payments VALUES 
        ('PAY_5', 'ACC_2', 15000.0);
    """)

    investigator = StatisticalInvestigator(con=con)
    res = investigator.test_simpsons_paradox()

    # Pre-period recovery rate: exactly 20,000 / 50,000 = 40.0%
    # If fanout occurred, exposure would be 200,000 (4 * 50,000) -> 20,000 / 200,000 = 10.0%
    assert res["aggregate_pre_rate"] == 40.0, f"Expected 40.0% pre-period rate, got {res['aggregate_pre_rate']}% (fanout detected if 10.0%)"
    assert res["aggregate_post_rate"] == 25.0, f"Expected 25.0% post-period rate, got {res['aggregate_post_rate']}%"
