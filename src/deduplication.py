"""Deduplication and forensic payment audit engine."""

from typing import Dict, Any
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class DeduplicationEngine:
    """Detects, classifies, and audits payment duplications, retries, and reversals."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()

    def run_deduplication(self) -> pd.DataFrame:
        """Executes deduplication logic and populates payment_deduplication_log."""
        sql_path = settings.sql_dir / "04_deduplication.sql"
        try:
            if sql_path.exists():
                with open(sql_path, "r", encoding="utf-8") as f:
                    self.con.execute(f.read())
        except Exception as e:
            logger.debug(f"Could not execute deduplication DDL (e.g. read-only connection): {e}")
        
        try:
            return self.con.execute("SELECT * FROM v_payment_deduplication_audit;").fetchdf()
        except Exception as e:
            logger.warning(f"Error querying deduplication audit: {e}")
            return pd.DataFrame()

    def get_inflation_impact(self) -> Dict[str, Any]:
        """Calculates recovery inflation percentage caused by naive duplicate counting."""
        try:
            res = self.con.execute("SELECT * FROM v_forensic_recovery_inflation;").fetchone()
            if res:
                return {
                    "naive_gross_collections_inr": float(res[0] or 0.0),
                    "canonical_collections_inr": float(res[1] or 0.0),
                    "total_overstatement_inr": float(res[2] or 0.0),
                    "recovery_inflation_pct": float(res[3] or 0.0)
                }
        except Exception as e:
            logger.warning(f"Error querying recovery inflation: {e}")
        
        return {
            "naive_gross_collections_inr": 0.0,
            "canonical_collections_inr": 0.0,
            "total_overstatement_inr": 0.0,
            "recovery_inflation_pct": 0.0
        }
