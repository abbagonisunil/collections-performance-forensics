"""Unit tests for counterfactual estimation and causal inference."""

import pytest
import duckdb
import pandas as pd
from src.counterfactual import CounterfactualAnalyzer


def test_counterfactual_unpopulated_returns_awaiting_data(in_memory_db):
    """Verifies that an unpopulated database returns an explicit AWAITING_REAL_DATA status
    with None for statistical estimates, never fabricating fictional numbers.
    """
    con = in_memory_db
    cf = CounterfactualAnalyzer(con=con)
    res = cf.estimate_difference_in_differences()

    assert res["analysis_status"] == "AWAITING_REAL_DATA"
    assert res["estimate"] is None
    assert res["standard_error"] is None
    assert res["p_value"] is None
    assert res["incremental_recovery_inr"] is None
    assert "limitations" in res
    assert "assumptions" in res


def test_counterfactual_estimation_on_synthetic_panel():
    """Verifies that when a valid 2x2 panel is supplied, DiD computes genuine estimates
    and verifies that monetary counterfactual is derived from eligible exposure and estimated effect.
    """
    con = duckdb.connect(":memory:")
    # Create required analytical schemas
    con.execute("""
        CREATE TABLE dim_account (
            account_id VARCHAR,
            due_date DATE,
            opening_principal DOUBLE
        );
        CREATE TABLE clean_payments (
            account_id VARCHAR,
            amount_paid DOUBLE
        );
        CREATE TABLE features_account_level (
            account_id VARCHAR,
            targeted_in_post_period INTEGER
        );
    """)

    # Populate 2x2 panel: 50 control accounts, 50 treatment accounts
    # Control Pre (due < 2024-07-01, targeted=0): recovery rate ~ 10%
    # Control Post (due >= 2024-07-01, targeted=0): recovery rate ~ 12% (+2 pp trend)
    # Treatment Pre (due < 2024-07-01, targeted=1): recovery rate ~ 10%
    # Treatment Post (due >= 2024-07-01, targeted=1): recovery rate ~ 15% (+5 pp total -> +3 pp DiD effect)

    rows_acc = []
    rows_pay = []
    rows_feat = []

    # 25 Control Pre
    for i in range(1, 26):
        aid = f"C_PRE_{i}"
        rows_acc.append((aid, "2024-03-01", 10000.0))
        rows_pay.append((aid, 1000.0)) # 10%
        rows_feat.append((aid, 0))

    # 25 Control Post
    for i in range(1, 26):
        aid = f"C_POST_{i}"
        rows_acc.append((aid, "2024-08-01", 10000.0))
        rows_pay.append((aid, 1200.0)) # 12%
        rows_feat.append((aid, 0))

    # 25 Treatment Pre
    for i in range(1, 26):
        aid = f"T_PRE_{i}"
        rows_acc.append((aid, "2024-03-01", 10000.0))
        rows_pay.append((aid, 1000.0)) # 10%
        rows_feat.append((aid, 1))

    # 25 Treatment Post
    for i in range(1, 26):
        aid = f"T_POST_{i}"
        rows_acc.append((aid, "2024-08-01", 10000.0))
        rows_pay.append((aid, 1500.0)) # 15%
        rows_feat.append((aid, 1))

    con.executemany("INSERT INTO dim_account VALUES (?, ?, ?);", rows_acc)
    con.executemany("INSERT INTO clean_payments VALUES (?, ?);", rows_pay)
    con.executemany("INSERT INTO features_account_level VALUES (?, ?);", rows_feat)

    cf = CounterfactualAnalyzer(con=con)
    res = cf.estimate_difference_in_differences()

    assert res["analysis_status"] == "COMPUTED_FROM_DATA"
    # DiD: (15% - 10%) - (12% - 10%) = +3.0 percentage points
    assert abs(res["estimate"] - 3.0) < 0.1
    assert res["standard_error"] is not None
    assert res["ci_95_lower_pp"] <= res["ci_95_upper_pp"]
    assert res["observed_post_recovery_inr"] == 25 * 1500.0  # ₹37,500
    # Counterfactual rate = 10% (T pre) + 2% (C diff) = 12%
    # Counterfactual recovery = 25 * 10000 * 12% = ₹30,000
    assert abs(res["counterfactual_baseline_recovery_inr"] - 30000.0) < 1.0
    # Incremental causal recovery = 37500 - 30000 = ₹7,500
    assert abs(res["incremental_recovery_inr"] - 7500.0) < 1.0


def test_missing_targeting_history_returns_identification_not_supported():
    """Verifies that if accounts exist but targeting exposure history is unpopulated,
    the analyzer explicitly returns IDENTIFICATION_NOT_SUPPORTED rather than guessing.
    """
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE dim_account (account_id VARCHAR, due_date DATE, opening_principal DOUBLE);
        CREATE TABLE clean_payments (account_id VARCHAR, amount_paid DOUBLE);
        INSERT INTO dim_account VALUES ('A1', '2024-03-01', 1000.0), ('A2', '2024-08-01', 2000.0);
    """)
    cf = CounterfactualAnalyzer(con=con)
    res = cf.estimate_difference_in_differences()

    assert res["analysis_status"] == "IDENTIFICATION_NOT_SUPPORTED"
    assert res["estimate"] is None
    assert res["p_value"] is None
    assert "Daily targeting history" in res["limitations"][0]


def test_single_pre_period_reports_parallel_trends_limitation():
    """Verifies that when only 1 pre-period cohort exists, the analyzer reports
    that formal parallel pre-trends test requires >= 2 pre-periods.
    """
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE dim_account (account_id VARCHAR, due_date DATE, opening_principal DOUBLE);
        CREATE TABLE clean_payments (account_id VARCHAR, amount_paid DOUBLE);
        CREATE TABLE features_account_level (account_id VARCHAR, targeted_in_post_period INTEGER);
    """)
    # 20 accounts across 1 pre-month and 1 post-month
    for i in range(10):
        con.execute(f"INSERT INTO dim_account VALUES ('C_PRE_{i}', '2024-04-01', 5000.0);")
        con.execute(f"INSERT INTO features_account_level VALUES ('C_PRE_{i}', 0);")
        con.execute(f"INSERT INTO dim_account VALUES ('C_POST_{i}', '2024-09-01', 5000.0);")
        con.execute(f"INSERT INTO features_account_level VALUES ('C_POST_{i}', 0);")
        con.execute(f"INSERT INTO dim_account VALUES ('T_PRE_{i}', '2024-04-01', 5000.0);")
        con.execute(f"INSERT INTO features_account_level VALUES ('T_PRE_{i}', 1);")
        con.execute(f"INSERT INTO dim_account VALUES ('T_POST_{i}', '2024-09-01', 5000.0);")
        con.execute(f"INSERT INTO features_account_level VALUES ('T_POST_{i}', 1);")

    cf = CounterfactualAnalyzer(con=con)
    res = cf.estimate_difference_in_differences()

    assert res["analysis_status"] == "COMPUTED_FROM_DATA"
    assert "requires >= 2 pre-periods" in res["pre_treatment_trend_result"]
