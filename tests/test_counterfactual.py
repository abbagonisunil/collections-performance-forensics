"""Unit tests for counterfactual estimation and causal inference."""

import pytest
import duckdb
from src.counterfactual import CounterfactualAnalyzer


def test_counterfactual_estimation(populated_test_db):
    """Verifies that counterfactual analyzer computes DiD estimates with valid intervals."""
    con = populated_test_db
    cf = CounterfactualAnalyzer(con=con)
    res = cf.estimate_difference_in_differences()

    assert "did_effect_percentage_points" in res
    assert "ci_95_lower_pp" in res
    assert "ci_95_upper_pp" in res
    assert res["ci_95_lower_pp"] <= res["ci_95_upper_pp"]
    assert "business_interpretation" in res
    assert len(res["business_interpretation"]) > 20
