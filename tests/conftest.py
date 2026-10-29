"""Pytest configuration and test database fixtures."""

import sys
from pathlib import Path
import pytest
import duckdb
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.utils import execute_sql_file
from tests.fixtures.synthetic_fixtures import (
    SYNTHETIC_PAYMENTS_DATA,
    SYNTHETIC_ACCOUNTS_DATA,
    SYNTHETIC_CALLS_DATA,
    SYNTHETIC_DISPOSITIONS_DATA,
    SYNTHETIC_PROMISES_DATA,
)


@pytest.fixture(scope="function")
def in_memory_db() -> duckdb.DuckDBPyConnection:
    """Provides a fresh, empty in-memory DuckDB instance with schemas initialized."""
    con = duckdb.connect(":memory:")
    # Initialize all empty raw tables from source_inventory.yaml
    sources = settings.inventory.get("sources", {})
    for src_name, spec in sources.items():
        cols = spec.get("columns", {})
        if cols:
            col_defs = ", ".join([f"{col} {dtype}" for col, dtype in cols.items()])
            con.execute(f"CREATE TABLE raw_{src_name} ({col_defs});")
    return con


@pytest.fixture(scope="function")
def populated_test_db(in_memory_db: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyConnection:
    """Populates the in-memory test database with synthetic mock fixtures strictly for unit tests."""
    con = in_memory_db

    # Insert mock payments
    df_pay = pd.DataFrame(SYNTHETIC_PAYMENTS_DATA)
    con.execute("INSERT INTO raw_payments SELECT * FROM df_pay;")

    # Insert mock accounts
    df_acc = pd.DataFrame(SYNTHETIC_ACCOUNTS_DATA)
    con.execute("INSERT INTO raw_accounts SELECT * FROM df_acc;")

    # Insert mock calls
    df_calls = pd.DataFrame(SYNTHETIC_CALLS_DATA)
    con.execute("INSERT INTO raw_calls SELECT * FROM df_calls;")

    # Insert mock dispositions
    df_disp = pd.DataFrame(SYNTHETIC_DISPOSITIONS_DATA)
    con.execute("INSERT INTO raw_call_dispositions SELECT * FROM df_disp;")

    # Insert mock promises
    df_ptp = pd.DataFrame(SYNTHETIC_PROMISES_DATA)
    con.execute("INSERT INTO raw_promises_to_pay SELECT * FROM df_ptp;")

    # Execute staging and base views
    execute_sql_file(con, settings.sql_dir / "01_staging.sql")
    execute_sql_file(con, settings.sql_dir / "03_entity_resolution.sql")
    execute_sql_file(con, settings.sql_dir / "04_deduplication.sql")

    return con
