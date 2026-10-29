"""Source data profiling and exploratory schema audit module."""

from typing import Dict, Any, List
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class SourceProfiler:
    """Profiles raw and staged tables for completeness, grain, and key constraints."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()

    def profile_all_sources(self) -> pd.DataFrame:
        """Profiles row counts, column counts, and key stats across all raw sources."""
        sources = settings.inventory.get("sources", {})
        records = []

        for source_name, spec in sources.items():
            table_name = f"raw_{source_name}"
            pk_cols = spec.get("primary_key", [])
            ts_cols = spec.get("timestamp_fields", {})

            try:
                # Check if table exists
                tbl_exists = self.con.execute(f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = '{table_name}';
                """).fetchone()[0] > 0

                if not tbl_exists:
                    records.append({
                        "source_name": source_name,
                        "table_name": table_name,
                        "row_count": 0,
                        "column_count": 0,
                        "pk_columns": ", ".join(pk_cols),
                        "pk_duplicate_count": 0,
                        "earliest_ts": None,
                        "latest_ts": None,
                        "date_span_days": 0,
                        "status": "NOT_LOADED"
                    })
                    continue

                row_count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                cols = self.con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
                col_count = len(cols)

                # Check PK uniqueness if rows exist
                pk_dup_count = 0
                if row_count > 0 and pk_cols:
                    pk_str = ", ".join(pk_cols)
                    dup_query = f"""
                        SELECT COUNT(*) FROM (
                            SELECT {pk_str}, COUNT(*) AS cnt 
                            FROM {table_name} 
                            GROUP BY {pk_str} 
                            HAVING COUNT(*) > 1
                        );
                    """
                    pk_dup_count = self.con.execute(dup_query).fetchone()[0]

                # Check date range from first timestamp column
                earliest_ts = None
                latest_ts = None
                span_days = 0
                if row_count > 0 and ts_cols:
                    first_ts_col = list(ts_cols.keys())[0]
                    # verify column exists
                    col_names = [c[1] for c in cols]
                    if first_ts_col in col_names:
                        ts_res = self.con.execute(f"""
                            SELECT MIN(CAST({first_ts_col} AS TIMESTAMP)), MAX(CAST({first_ts_col} AS TIMESTAMP))
                            FROM {table_name}
                            WHERE {first_ts_col} IS NOT NULL;
                        """).fetchone()
                        earliest_ts = ts_res[0]
                        latest_ts = ts_res[1]
                        if earliest_ts and latest_ts:
                            span_days = (latest_ts - earliest_ts).days

                records.append({
                    "source_name": source_name,
                    "table_name": table_name,
                    "row_count": row_count,
                    "column_count": col_count,
                    "pk_columns": ", ".join(pk_cols),
                    "pk_duplicate_count": pk_dup_count,
                    "earliest_ts": earliest_ts,
                    "latest_ts": latest_ts,
                    "date_span_days": span_days,
                    "status": "PROFILED" if row_count > 0 else "EMPTY"
                })

            except Exception as e:
                logger.warning(f"Error profiling {source_name}: {e}")
                records.append({
                    "source_name": source_name,
                    "table_name": table_name,
                    "row_count": 0,
                    "column_count": 0,
                    "pk_columns": ", ".join(pk_cols),
                    "pk_duplicate_count": 0,
                    "earliest_ts": None,
                    "latest_ts": None,
                    "date_span_days": 0,
                    "status": f"ERROR: {str(e)[:40]}"
                })

        return pd.DataFrame(records)


def profile_sources() -> pd.DataFrame:
    """Convenience function to run source profiling."""
    profiler = SourceProfiler()
    return profiler.profile_all_sources()
