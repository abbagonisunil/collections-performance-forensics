"""Master pipeline orchestrator for Collections Performance Forensics."""

import sys
from pathlib import Path
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

    def __init__(self):
        self.con = get_db_connection()
        self.outputs_dir = settings.outputs_dir
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Executes all forensic pipeline stages sequentially."""
        logger.info("=== STARTING COLLECTIONS PERFORMANCE FORENSICS PIPELINE ===")

        # Stage 1: Ingestion & Schema Discovery
        logger.info("--- Stage 1: Ingestion & Schema Discovery ---")
        ingestion = IngestionEngine(con=self.con)
        ingestion_results = ingestion.run_ingestion()

        # Stage 2: Source Profiling
        logger.info("--- Stage 2: Source Profiling ---")
        profiler = SourceProfiler(con=self.con)
        profile_df = profiler.profile_all_sources()
        profile_df.to_csv(self.outputs_dir / "source_profiling_summary.csv", index=False)
        logger.info(f"Source profiling completed: {len(profile_df)} sources profiled.")

        # Stage 3: Analytical Transformations (Staging -> Clean -> Golden -> Features)
        logger.info("--- Stage 3: Transformations & Golden Layer Generation ---")
        transform = TransformationOrchestrator(con=self.con)
        transform.run_staging()

        # Stage 4: Entity Resolution & Crosswalks
        logger.info("--- Stage 4: Entity Resolution & Crosswalks ---")
        resolver = EntityResolver(con=self.con)
        resolver.build_crosswalks()

        # Stage 5: Payment Deduplication & Replay Audit
        logger.info("--- Stage 5: Deduplication & Overstatement Audit ---")
        dedup = DeduplicationEngine(con=self.con)
        dedup_df = dedup.run_deduplication()
        if not dedup_df.empty:
            dedup_df.to_csv(self.outputs_dir / "payment_deduplication_audit.csv", index=False)
        inflation_stats = dedup.get_inflation_impact()
        logger.info(f"Recovery inflation audit: {inflation_stats.get('recovery_inflation_pct', 0.0)}% apparent inflation.")

        # Stage 6: Build Clean and Golden Datasets
        logger.info("--- Stage 6: Clean Models and Golden Dimensions/Facts ---")
        transform.run_clean_models()
        transform.run_golden_dataset()
        transform.run_features()

        # Stage 7: Timestamp Normalization & Calling Window Audit
        logger.info("--- Stage 7: Timestamp Normalization & Compliance ---")
        ts_normalizer = TimestampNormalizer(con=self.con)
        calling_hours_df = ts_normalizer.audit_calling_hours_compliance()
        if not calling_hours_df.empty:
            calling_hours_df.to_csv(self.outputs_dir / "calling_hours_compliance.csv", index=False)

        # Stage 8: Payment Attribution Bridge (4 Models)
        logger.info("--- Stage 8: Omnichannel Payment Attribution ---")
        attribution = AttributionEngine(con=self.con)
        attribution_df = attribution.run_attribution()
        if not attribution_df.empty:
            attribution_df.to_csv(self.outputs_dir / "payment_attribution_comparison.csv", index=False)

        # Stage 9: Metrics Calculation & 12-Month Performance Reconstruction
        logger.info("--- Stage 9: Metrics Calculation & 11% Claim Audit ---")
        metrics_engine = MetricsEngine(con=self.con)
        monthly_df = metrics_engine.calculate_metrics()
        if not monthly_df.empty:
            monthly_df.to_csv(self.outputs_dir / "monthly_performance_reconstruction.csv", index=False)
        claim_verdict = metrics_engine.evaluate_11_pct_claim()
        logger.info(f"Verdict on 11% claim: {claim_verdict.get('forensic_verdict')}")

        # Stage 10: Statistical Driver Analysis & Biases
        logger.info("--- Stage 10: 13-Dimension Driver Decomposition & Statistical Risks ---")
        stat_engine = StatisticalInvestigator(con=self.con)
        driver_dfs = stat_engine.run_driver_analysis()
        findings_df = stat_engine.generate_findings_table()
        findings_df.to_csv(self.outputs_dir / "forensic_investigation_summary.csv", index=False)

        # Stage 11: Counterfactual Analysis (Difference-in-Differences)
        logger.info("--- Stage 11: Counterfactual Analysis (Targeting Shift) ---")
        counterfactual = CounterfactualAnalyzer(con=self.con)
        cf_results = counterfactual.estimate_difference_in_differences()
        cf_df = pd.DataFrame([cf_results])
        cf_df.to_csv(self.outputs_dir / "counterfactual_estimates.csv", index=False)

        # Stage 12: ₹10 Crore Investment Financial Model
        logger.info("--- Stage 12: ₹10 Cr Capital Allocation Model ---")
        invest_model = InvestmentModel()
        invest_df = invest_model.evaluate_all()
        invest_df.to_csv(self.outputs_dir / "investment_model_scenarios.csv", index=False)

        # Stage 13: End-to-End Reconciliation
        logger.info("--- Stage 13: End-to-End Reconciliation & Invariants Check ---")
        monetary_trail, dedup_balance, invariant_failures = metrics_engine.run_reconciliation()
        if not monetary_trail.empty:
            monetary_trail.to_csv(self.outputs_dir / "reconciliation_monetary_trail.csv", index=False)
        if not invariant_failures.empty:
            logger.warning(f"Production invariant failures detected: {len(invariant_failures)}")
            invariant_failures.to_csv(self.outputs_dir / "invariant_failures.csv", index=False)
        else:
            logger.info("All production invariants satisfied.")

        logger.info("=== PIPELINE EXECUTION COMPLETED SUCCESSFULLY ===")


def main():
    pipeline = ForensicPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
