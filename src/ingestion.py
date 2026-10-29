"""Data ingestion module: discovers, validates, and loads raw source files into DuckDB."""

from pathlib import Path
from typing import Dict, List, Any
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection

EXPECTED_SOURCES = [
    "borrowers",
    "accounts",
    "agents",
    "agent_sessions",
    "campaigns",
    "daily_targeting",
    "calls",
    "call_attempts",
    "call_dispositions",
    "whatsapp_events",
    "sms_events",
    "field_visits",
    "promises_to_pay",
    "payments",
    "vendor_telephony",
    "complaints",
    "account_status_history",
]


class IngestionEngine:
    """Manages raw dataset discovery, schema initialization, and loading."""

    def __init__(self, raw_dir: Path = None, con: duckdb.DuckDBPyConnection = None):
        self.raw_dir = raw_dir or settings.raw_data_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.con = con or get_db_connection()

    def discover_raw_files(self) -> Dict[str, Dict[str, Any]]:
        """Scans the raw data directory and matches files to expected sources."""
        inventory = {}
        for source in EXPECTED_SOURCES:
            matched_files = list(self.raw_dir.glob(f"{source}.*")) + list(self.raw_dir.glob(f"raw_{source}.*"))
            # Exclude .gitkeep
            valid_files = [f for f in matched_files if f.suffix.lower() in [".csv", ".parquet", ".json", ".jsonl"]]
            
            if valid_files:
                target_file = valid_files[0]
                inventory[source] = {
                    "source_name": source,
                    "status": "AVAILABLE",
                    "file_path": str(target_file),
                    "file_format": target_file.suffix.lower().replace(".", ""),
                    "file_size_bytes": target_file.stat().st_size,
                }
            else:
                inventory[source] = {
                    "source_name": source,
                    "status": "AWAITING_DATA",
                    "file_path": None,
                    "file_format": None,
                    "file_size_bytes": 0,
                }
        return inventory

    def initialize_empty_schema(self, source_name: str) -> None:
        """Initializes an empty typed table in DuckDB based on source_inventory.yaml."""
        spec = settings.get_source_spec(source_name)
        columns = spec.get("columns", {})
        if not columns:
            return

        col_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        table_name = f"raw_{source_name}"
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs});"
        self.con.execute(create_sql)

    def load_source(self, source_name: str, file_path: Path) -> int:
        """Loads a discovered raw file into DuckDB with schema enforcement."""
        table_name = f"raw_{source_name}"
        ext = file_path.suffix.lower()
        logger.info(f"Ingesting {source_name} from {file_path.name} into {table_name}...")

        if ext == ".csv":
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}', header=True);
            """)
        elif ext == ".parquet":
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{file_path}');
            """)
        elif ext in [".json", ".jsonl"]:
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_json_auto('{file_path}');
            """)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info(f"Loaded {count} rows into {table_name}.")
        return count

    def run_ingestion(self) -> Dict[str, Any]:
        """Discovers and ingests all available raw source files.

        Initializes empty compliant schemas for unsupplied files.
        """
        discovery = self.discover_raw_files()
        results = {}
        available_count = 0

        for source_name, info in discovery.items():
            if info["status"] == "AVAILABLE" and info["file_path"]:
                row_count = self.load_source(source_name, Path(info["file_path"]))
                info["row_count"] = row_count
                available_count += 1
            else:
                self.initialize_empty_schema(source_name)
                info["row_count"] = 0
            results[source_name] = info

        logger.info(f"Ingestion completed: {available_count}/{len(EXPECTED_SOURCES)} sources available.")
        return results


def run_ingestion() -> Dict[str, Any]:
    """Convenience function to run ingestion engine."""
    engine = IngestionEngine()
    return engine.run_ingestion()
