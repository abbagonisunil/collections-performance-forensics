"""Master pipeline orchestrator for Collections Performance Forensics."""

import sys
from pathlib import Path
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection
from src.ingestion import IngestionEngine
from src.profiling import SourceProfiler
from src.transformations import TransformationOrchestrator
from src.entity_resolution import EntityResolver
from src.deduplication import DeduplicationEngine
from src.timestamp_normalization import TimestampNormalizer
from src.payment_attribution import AttributionEngine
from src.metrics import MetricsEngine
from src.statistical_analysis import StatisticalInvestigator
from src.counterfactual import CounterfactualAnalyzer
from src.investment_model import InvestmentModel


class ForensicPipeline:
    """Executes the full end-to-end analytical forensics and modeling pipeline."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()
        self.outputs_dir = settings.outputs_dir
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        """Executes all forensic pipeline stages sequentially and returns a structured execution report."""
        logger.info("=== STARTING COLLECTIONS PERFORMANCE FORENSICS PIPELINE ===")
        stages = {}
        critical_error_occurred = False

        # Stage 1: Ingestion & Schema Discovery
        logger.info("--- Stage 1: Ingestion & Schema Discovery ---")
        try:
            ingestion = IngestionEngine(con=self.con)
            ingestion_results = ingestion.run_ingestion()
            available_sources = sum(1 for v in ingestion_results.values() if v.get("status") == "INGESTED")
            stages["01_ingestion"] = {
                "status": "SUCCESS" if available_sources > 0 else "AWAITING_REAL_DATA",
                "sources_available": available_sources,
                "total_expected": 17
            }
        except Exception as e:
            logger.error(f"Stage 1 Ingestion failed: {e}", exc_info=True)
            stages["01_ingestion"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 2: Source Profiling
        logger.info("--- Stage 2: Source Profiling ---")
        try:
            profiler = SourceProfiler(con=self.con)
            profile_df = profiler.profile_all_sources()
            profile_df.to_csv(self.outputs_dir / "source_profiling_summary.csv", index=False)
            stages["02_profiling"] = {
                "status": "SUCCESS",
                "sources_profiled": len(profile_df)
            }
            logger.info(f"Source profiling completed: {len(profile_df)} sources profiled.")
        except Exception as e:
            logger.error(f"Stage 2 Profiling failed: {e}", exc_info=True)
            stages["02_profiling"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 3: Analytical Transformations (Staging -> Clean -> Golden -> Features)
        logger.info("--- Stage 3: Transformations & Golden Layer Generation ---")
        try:
            transform = TransformationOrchestrator(con=self.con)
            transform.run_staging()
            stages["03_staging"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 3 Staging failed: {e}", exc_info=True)
            stages["03_staging"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 4: Entity Resolution & Crosswalks
        logger.info("--- Stage 4: Entity Resolution & Crosswalks ---")
        try:
            resolver = EntityResolver(con=self.con)
            resolver.build_crosswalks()
            stages["04_entity_resolution"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 4 Entity Resolution failed: {e}", exc_info=True)
            stages["04_entity_resolution"] = {"status": "FAILED", "error": str(e)}

        # Stage 5: Payment Deduplication & Replay Audit
        logger.info("--- Stage 5: Deduplication & Overstatement Audit ---")
        try:
            dedup = DeduplicationEngine(con=self.con)
            dedup_df = dedup.run_deduplication()
            if not dedup_df.empty:
                dedup_df.to_csv(self.outputs_dir / "payment_deduplication_audit.csv", index=False)
            inflation_stats = dedup.get_inflation_impact()
            logger.info(f"Recovery inflation audit: {inflation_stats.get('recovery_inflation_pct', 0.0)}% apparent inflation.")
            stages["05_deduplication"] = {
                "status": "SUCCESS",
                "records_audited": len(dedup_df),
                "apparent_inflation_pct": inflation_stats.get("recovery_inflation_pct", 0.0)
            }
        except Exception as e:
            logger.error(f"Stage 5 Deduplication failed: {e}", exc_info=True)
            stages["05_deduplication"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 6: Build Clean and Golden Datasets
        logger.info("--- Stage 6: Clean Models and Golden Dimensions/Facts ---")
        try:
            transform.run_clean_models()
            transform.run_golden_dataset()
            transform.run_features()
            stages["06_golden_dataset"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 6 Golden Dataset failed: {e}", exc_info=True)
            stages["06_golden_dataset"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 7: Timestamp Normalization & Calling Window Audit
        logger.info("--- Stage 7: Timestamp Normalization & Compliance ---")
        try:
            ts_normalizer = TimestampNormalizer(con=self.con)
            calling_hours_df = ts_normalizer.audit_calling_hours_compliance()
            if not calling_hours_df.empty:
                calling_hours_df.to_csv(self.outputs_dir / "calling_hours_compliance.csv", index=False)
            stages["07_compliance"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 7 Compliance failed: {e}", exc_info=True)
            stages["07_compliance"] = {"status": "FAILED", "error": str(e)}

        # Stage 8: Payment Attribution Bridge (4 Models)
        logger.info("--- Stage 8: Omnichannel Payment Attribution ---")
        try:
            attribution = AttributionEngine(con=self.con)
            attribution_df = attribution.run_attribution()
            if not attribution_df.empty:
                attribution_df.to_csv(self.outputs_dir / "payment_attribution_comparison.csv", index=False)
            stages["08_attribution"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 8 Attribution failed: {e}", exc_info=True)
            stages["08_attribution"] = {"status": "FAILED", "error": str(e)}

        # Stage 9: Metrics Calculation & 12-Month Performance Reconstruction
        logger.info("--- Stage 9: Metrics Calculation & 11% Claim Audit ---")
        claim_verdict = {"forensic_verdict": "NOT_VERIFIABLE"}
        try:
            metrics_engine = MetricsEngine(con=self.con)
            monthly_df = metrics_engine.calculate_metrics()
            if not monthly_df.empty:
                monthly_df.to_csv(self.outputs_dir / "monthly_performance_reconstruction.csv", index=False)
            claim_verdict = metrics_engine.evaluate_11_pct_claim()
            logger.info(f"Verdict on 11% claim: {claim_verdict.get('forensic_verdict')}")
            stages["09_metrics"] = {
                "status": "SUCCESS",
                "verdict_11_pct_claim": claim_verdict.get("forensic_verdict")
            }
        except Exception as e:
            logger.error(f"Stage 9 Metrics failed: {e}", exc_info=True)
            stages["09_metrics"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Stage 10: Statistical Driver Analysis & Biases
        logger.info("--- Stage 10: 13-Dimension Driver Decomposition & Statistical Risks ---")
        try:
            stat_engine = StatisticalInvestigator(con=self.con)
            driver_dfs = stat_engine.run_driver_analysis()
            findings_df = stat_engine.generate_findings_table()
            findings_df.to_csv(self.outputs_dir / "forensic_investigation_summary.csv", index=False)
            stages["10_driver_analysis"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 10 Driver Analysis failed: {e}", exc_info=True)
            stages["10_driver_analysis"] = {"status": "FAILED", "error": str(e)}

        # Stage 11: Counterfactual Analysis (Difference-in-Differences)
        logger.info("--- Stage 11: Counterfactual Analysis (Targeting Shift) ---")
        try:
            counterfactual = CounterfactualAnalyzer(con=self.con)
            cf_results = counterfactual.estimate_difference_in_differences()
            cf_df = pd.DataFrame([cf_results])
            cf_df.to_csv(self.outputs_dir / "counterfactual_estimates.csv", index=False)
            stages["11_counterfactual"] = {
                "status": cf_results.get("analysis_status", "AWAITING_REAL_DATA")
            }
        except Exception as e:
            logger.error(f"Stage 11 Counterfactual failed: {e}", exc_info=True)
            stages["11_counterfactual"] = {"status": "FAILED", "error": str(e)}

        # Stage 12: ₹10 Crore Investment Financial Model
        logger.info("--- Stage 12: ₹10 Cr Capital Allocation Model ---")
        try:
            invest_model = InvestmentModel()
            invest_df = invest_model.evaluate_all()
            invest_df.to_csv(self.outputs_dir / "investment_model_scenarios.csv", index=False)
            stages["12_investment_model"] = {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Stage 12 Investment Model failed: {e}", exc_info=True)
            stages["12_investment_model"] = {"status": "FAILED", "error": str(e)}

        # Stage 13: End-to-End Reconciliation
        logger.info("--- Stage 13: End-to-End Reconciliation & Invariants Check ---")
        invariant_count = 0
        try:
            monetary_trail, dedup_balance, invariant_failures = metrics_engine.run_reconciliation()
            if not monetary_trail.empty:
                monetary_trail.to_csv(self.outputs_dir / "reconciliation_monetary_trail.csv", index=False)
            if not invariant_failures.empty:
                invariant_count = len(invariant_failures)
                logger.warning(f"Production invariant failures detected: {invariant_count}")
                invariant_failures.to_csv(self.outputs_dir / "invariant_failures.csv", index=False)
            else:
                logger.info("All production invariants satisfied.")
            stages["13_reconciliation"] = {
                "status": "SUCCESS" if invariant_count == 0 else "PARTIAL_SUCCESS",
                "invariant_failures_count": invariant_count
            }
        except Exception as e:
            logger.error(f"Stage 13 Reconciliation failed: {e}", exc_info=True)
            stages["13_reconciliation"] = {"status": "FAILED", "error": str(e)}
            critical_error_occurred = True

        # Determine overall pipeline status
        if critical_error_occurred:
            overall_status = "FAILED"
        elif stages.get("01_ingestion", {}).get("sources_available", 0) == 0:
            overall_status = "AWAITING_REAL_DATA"
        elif invariant_count > 0:
            overall_status = "PARTIAL_SUCCESS"
        else:
            overall_status = "SUCCESS"

        logger.info(f"=== PIPELINE EXECUTION COMPLETED: {overall_status} ===")

        return {
            "overall_status": overall_status,
            "stages": stages,
            "verdict_11_pct_claim": claim_verdict.get("forensic_verdict"),
            "invariant_failures_count": invariant_count
        }


def main():
    pipeline = ForensicPipeline()
    report = pipeline.run()
    if report["overall_status"] == "FAILED":
        sys.exit(1)


if __name__ == "__main__":
    main()
