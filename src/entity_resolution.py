"""Entity resolution module: links identifiers across Borrowers, Agents, and Vendor Telephony."""

from typing import Dict, Any
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class EntityResolver:
    """Manages crosswalk generation and entity linkage."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()

    def build_crosswalks(self) -> Dict[str, int]:
        """Executes entity resolution SQL and populates crosswalk tables."""
        sql_path = settings.sql_dir / "03_entity_resolution.sql"
        if sql_path.exists():
            with open(sql_path, "r", encoding="utf-8") as f:
                self.con.execute(f.read())

        stats = {}
        for table in ["dim_borrower_crosswalk", "dim_agent_crosswalk", "ref_disposition_crosswalk"]:
            try:
                cnt = self.con.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
                stats[table] = cnt
            except Exception:
                stats[table] = 0
        return stats

    def get_agent_resolution_summary(self) -> pd.DataFrame:
        """Audits agent alias resolution and multi-identifier consolidation."""
        try:
            query = """
                SELECT 
                    resolution_status,
                    COUNT(*) AS count_source_ids,
                    COUNT(DISTINCT canonical_agent_id) AS distinct_canonical_agents
                FROM dim_agent_crosswalk
                GROUP BY 1;
            """
            return self.con.execute(query).fetchdf()
        except Exception as e:
            logger.warning(f"Unable to retrieve agent resolution summary: {e}")
            return pd.DataFrame()
