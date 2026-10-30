"""Unit tests for statistical analysis and Kitagawa shift-share mix decomposition."""

import pytest
import numpy as np
from src.statistical_analysis import StatisticalInvestigator


def test_kitagawa_mix_decomposition_mathematical_identity():
    """Mathematically verifies that Kitagawa decomposition holds as an exact identity:
    Total Rate Change = Within-Segment Operational Effect + Between-Segment Mix Effect.
    """
    import duckdb
    investigator = StatisticalInvestigator(con=duckdb.connect(":memory:"))
    benchmark = investigator.get_benchmark_mix_decomposition()

    total_change = benchmark["total_change_pp"]
    within_effect = benchmark["within_operational_effect_pp"]
    between_effect = benchmark["between_mix_shift_effect_pp"]

    # Invariant: within + between must equal total change exactly
    assert abs((within_effect + between_effect) - total_change) < 1e-6

    # Verify documented benchmark properties
    assert benchmark["period_pre_rate_pct"] == 10.20
    assert benchmark["period_post_rate_pct"] == 15.20
    assert total_change == 5.00
    assert within_effect == 1.90
    assert between_effect == 3.10
    assert benchmark["pct_change_driven_by_mix"] == 62.0


def test_segment_level_rate_changes_bounded():
    """Verifies that non-early DPD cohorts have operational rate changes strictly below 1.2 pp."""
    import duckdb
    investigator = StatisticalInvestigator(con=duckdb.connect(":memory:"))
    benchmark = investigator.get_benchmark_mix_decomposition()
    segments = benchmark["segment_breakdown"]

    # DPD 31-60, 61-90, and 90+ must each have operational changes < 1.2 pp
    assert segments["DPD 31-60"]["rate_change_pp"] < 1.20
    assert segments["DPD 61-90"]["rate_change_pp"] < 1.20
    assert segments["DPD 90+"]["rate_change_pp"] < 1.20

    # Early DPD 1-30 drove the majority of within-cohort change
    assert segments["DPD 1-30"]["rate_change_pp"] == 1.80


def test_arbitrary_kitagawa_identity_randomized():
    """Tests the mathematical identity of Kitagawa decomposition on arbitrary random weights and rates."""
    np.random.seed(42)
    k = 5  # 5 segments
    w0 = np.random.dirichlet(np.ones(k))
    w1 = np.random.dirichlet(np.ones(k))
    r0 = np.random.uniform(0.05, 0.40, k)
    r1 = np.random.uniform(0.05, 0.40, k)

    R0 = np.sum(w0 * r0)
    R1 = np.sum(w1 * r1)
    delta_R = R1 - R0

    w_bar = 0.5 * (w0 + w1)
    r_bar = 0.5 * (r0 + r1)
    delta_r = r1 - r0
    delta_w = w1 - w0

    within = np.sum(w_bar * delta_r)
    between = np.sum(r_bar * delta_w)

    assert abs((within + between) - delta_R) < 1e-12, "Kitagawa decomposition identity violated!"
