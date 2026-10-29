"""Timestamp normalization, timezone conversion, and calling hours compliance."""

from typing import Dict, Any
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class TimestampNormalizer:
    """Standardizes event timestamps to UTC and evaluates local calling window adherence."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()
        self.local_tz = settings.local_timezone

    def audit_calling_hours_compliance(self) -> pd.DataFrame:
        """Audits calling hour distribution and flags potential regulatory non-compliance."""
        try:
            query = """
                SELECT 
                    is_rbi_compliant_calling_hour,
                    COUNT(*) AS total_calls,
                    COUNT(DISTINCT account_id) AS unique_accounts_called,
                    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_calls
                FROM clean_calls
                GROUP BY 1;
            """
            return self.con.execute(query).fetchdf()
        except Exception as e:
            logger.warning(f"Unable to audit calling hours: {e}")
            return pd.DataFrame()

    def audit_midnight_boundary_shifts(self) -> Dict[str, Any]:
        """Quantifies records that shift reporting dates when converting from UTC to local time."""
        try:
            query = """
                SELECT 
                    COUNT(*) AS total_calls,
                    SUM(CASE WHEN CAST(call_start_time AS DATE) != CAST(call_start_time + INTERVAL 5 HOUR 30 MINUTE AS DATE) THEN 1 ELSE 0 END) AS shifted_date_count
                FROM stg_calls;
            """
            res = self.con.execute(query).fetchone()
            if res and res[0] > 0:
                return {
                    "total_calls": res[0],
                    "shifted_date_count": res[1],
                    "shift_rate_pct": round(100.0 * res[1] / res[0], 2)
                }
        except Exception as e:
            logger.warning(f"Timestamp boundary shift audit: {e}")
        
        return {"total_calls": 0, "shifted_date_count": 0, "shift_rate_pct": 0.0}
