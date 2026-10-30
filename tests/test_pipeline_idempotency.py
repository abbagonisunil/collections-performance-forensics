"""Unit tests for pipeline idempotency and empty dashboard state handling."""

import pytest
import duckdb
from src.metrics import MetricsEngine
from src.deduplication import DeduplicationEngine
from src.statistical_analysis import StatisticalInvestigator
from src.counterfactual import CounterfactualAnalyzer
from src.investment_model import InvestmentModel


def test_empty_dashboard_state_handling(in_memory_db):
    """Verifies that all dashboard data engines handle empty states safely without throwing exceptions."""
    con = in_memory_db

    # 1. Metrics engine
    metrics_engine = MetricsEngine(con=con)
    claim_audit = metrics_engine.evaluate_11_pct_claim()
    assert claim_audit["forensic_verdict"] == "NOT_VERIFIABLE"
    assert claim_audit["evaluated_months_count"] == 0
    assert claim_audit["numerator_cash_recovered"] == 0.0

    # 2. Deduplication engine
    dedup_engine = DeduplicationEngine(con=con)
    inflation = dedup_engine.get_inflation_impact()
    assert inflation["naive_gross_collections_inr"] == 0.0
    assert inflation["canonical_collections_inr"] == 0.0
    assert inflation["recovery_inflation_pct"] == 0.0

    # 3. Statistical investigator
    stat_investigator = StatisticalInvestigator(con=con)
    mix = stat_investigator.calculate_mix_decomposition()
    assert mix["status"] == "AWAITING_REAL_DATA"
    assert mix["total_change_pp"] is None

    # 4. Counterfactual analyzer
    cf_analyzer = CounterfactualAnalyzer(con=con)
    cf_res = cf_analyzer.estimate_difference_in_differences()
    assert cf_res["analysis_status"] == "AWAITING_REAL_DATA"
    assert cf_res["estimate"] is None

    # 5. Investment model
    inv_model = InvestmentModel(capital_cr=10.0)
    rec = inv_model.get_recommended_allocation()
    assert rec["phase_1_capital_commitment_cr"] == 2.0


def test_pipeline_transformation_idempotency(in_memory_db):
    """Verifies that executing transformations multiple times is idempotent and produces no duplicates."""
    con = in_memory_db

    # Create dummy payment table
    con.execute("""
        CREATE TABLE stg_payments (
            payment_id VARCHAR,
            transaction_reference VARCHAR,
            account_id VARCHAR,
            amount_paid DOUBLE,
            principal_component DOUBLE,
            interest_component DOUBLE,
            fee_component DOUBLE,
            payment_method VARCHAR,
            payment_status VARCHAR,
            payment_timestamp TIMESTAMP,
            settlement_timestamp TIMESTAMP
        );
    """)

    con.execute("""
        INSERT INTO stg_payments VALUES 
        ('P1', 'UTR_001', 'ACC_1', 1000.0, 1000.0, 0.0, 0.0, 'UPI', 'SUCCESS', '2024-03-01 10:00:00', '2024-03-01 10:00:05');
    """)

    dedup = DeduplicationEngine(con=con)
    df1 = dedup.run_deduplication()
    cnt1 = con.execute("SELECT COUNT(*) FROM payment_deduplication_log;").fetchone()[0]

    # Run a second time
    df2 = dedup.run_deduplication()
    cnt2 = con.execute("SELECT COUNT(*) FROM payment_deduplication_log;").fetchone()[0]

    assert cnt1 == cnt2 == 1, "Deduplication execution must be strictly idempotent"


def test_pipeline_structured_execution_report(in_memory_db):
    """Verifies that ForensicPipeline returns structured stage statuses and reports AWAITING_REAL_DATA
    when raw sources are unpopulated without raising exceptions.
    """
    from src.pipeline import ForensicPipeline
    pipeline = ForensicPipeline(con=in_memory_db)
    report = pipeline.run()

    assert "overall_status" in report
    assert report["overall_status"] in ["AWAITING_REAL_DATA", "SUCCESS"]
    assert "stages" in report
    assert report["stages"]["01_ingestion"]["total_expected"] == 17
    assert report["stages"]["05_deduplication"]["status"] == "SUCCESS"
    assert report["stages"]["09_metrics"]["status"] == "SUCCESS"
    assert report["stages"]["13_reconciliation"]["status"] == "SUCCESS"
    assert report["verdict_11_pct_claim"] == "NOT_VERIFIABLE"
