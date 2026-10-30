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

    # Invariant: within + between must equal total change exactly
    assert abs((within_effect + between_effect) - total_change) < 1e-6
    assert res["identity_verified"] is True
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

        # Exact identity check within floating point tolerance
        assert abs((within_effect + between_effect) - total_change) < 1e-6
        assert res["identity_verified"] is True
