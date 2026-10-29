"""Analytical transformation orchestrator: Staging -> Clean -> Golden -> Features."""

from pathlib import Path
from typing import Dict, Any
import duckdb
from src.config import settings
from src.utils import logger, get_db_connection, execute_sql_file


class TransformationOrchestrator:
    """Executes sequence of SQL models building golden dimensional and fact layers."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()
        self.sql_dir = settings.sql_dir

    def run_staging(self) -> None:
        """Executes staging transformations."""
        execute_sql_file(self.con, self.sql_dir / "01_staging.sql")

    def run_clean_models(self) -> None:
        """Executes clean models transformations."""
        execute_sql_file(self.con, self.sql_dir / "05_clean_models.sql")

    def run_golden_dataset(self) -> None:
        """Executes golden dimensions and fact generation."""
        execute_sql_file(self.con, self.sql_dir / "06_golden_dataset.sql")

    def run_features(self) -> None:
        """Executes feature engineering SQL."""
        execute_sql_file(self.con, self.sql_dir / "08_features.sql")

    def run_all(self) -> Dict[str, int]:
        """Runs the complete transformation pipeline and returns record counts."""
        logger.info("Executing analytical transformation sequence...")
        self.run_staging()
        self.run_clean_models()
        self.run_golden_dataset()
        self.run_features()

        counts = {}
        for tbl in ["dim_account", "dim_agent", "fact_payment", "fact_interaction", "fact_ptp", "features_account_level"]:
            try:
                cnt = self.con.execute(f"SELECT COUNT(*) FROM {tbl};").fetchone()[0]
                counts[tbl] = cnt
            except Exception:
                counts[tbl] = 0
        return counts
