"""Omnichannel payment attribution bridge across multiple models and lookback windows."""

from typing import Dict, Any, List
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class AttributionEngine:
    """Calculates payment attribution across channels, ensuring non-fanout integrity."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()

    def run_attribution(self, window_days: int = 14) -> pd.DataFrame:
        """Executes payment attribution SQL and returns model comparison."""
        sql_path = settings.sql_dir / "07_payment_attribution.sql"
        if sql_path.exists():
            with open(sql_path, "r", encoding="utf-8") as f:
                self.con.execute(f.read())
        
        try:
            return self.con.execute("SELECT * FROM v_attribution_channel_comparison;").fetchdf()
        except Exception as e:
            logger.warning(f"Error querying attribution channel comparison: {e}")
            return pd.DataFrame()

    def compare_attribution_windows(self, windows: List[int] = None) -> pd.DataFrame:
        """Performs sensitivity analysis comparing channel recovery across 7d, 14d, and 30d windows."""
        windows = windows or [7, 14, 30]
        results = []
        for w in windows:
            try:
                query = f"""
                    WITH touches AS (
                        SELECT 
                            p.payment_id,
                            i.channel,
                            ROW_NUMBER() OVER (PARTITION BY p.payment_id ORDER BY i.interaction_timestamp DESC) AS rn,
                            p.amount_paid
                        FROM fact_payment p
                        JOIN fact_interaction i 
                            ON p.account_id = i.account_id 
                            AND i.interaction_timestamp <= p.payment_timestamp
                            AND i.interaction_timestamp >= (p.payment_timestamp - INTERVAL {w} DAY)
                    )
                    SELECT 
                        {w} AS lookback_window_days,
                        channel,
                        ROUND(SUM(amount_paid), 2) AS last_touch_recovered_inr
                    FROM touches
                    WHERE rn = 1
                    GROUP BY 1, 2;
                """
                df = self.con.execute(query).fetchdf()
                if not df.empty:
                    results.append(df)
            except Exception as e:
                logger.warning(f"Attribution window {w}d analysis failed: {e}")

        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
