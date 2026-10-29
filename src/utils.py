"""Utility functions, database connection management, and formatting helpers."""

import logging
from pathlib import Path
from typing import Optional
import duckdb
import pandas as pd
from src.config import settings

# Setup standard logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("collections_forensics")


def get_db_connection(db_path: Optional[Path] = None, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Returns a DuckDB database connection.

    If db_path is None, connects to the configured golden DuckDB file path.
    """
    target_path = db_path or settings.duckdb_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(target_path), read_only=read_only)


def format_currency_inr(amount: float) -> str:
    """Formats a numeric monetary amount into standard Indian Rupee notation (Cr / Lakh / K)."""
    if pd.isna(amount) or amount is None:
        return "₹0.00"
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amt >= 10_000_000:  # >= 1 Crore
        return f"{sign}₹{abs_amt / 10_000_000:.2f} Cr"
    elif abs_amt >= 100_000:   # >= 1 Lakh
        return f"{sign}₹{abs_amt / 100_000:.2f} L"
    elif abs_amt >= 1_000:     # >= 1 Thousand
        return f"{sign}₹{abs_amt / 1_000:.1f} K"
    else:
        return f"{sign}₹{abs_amt:.2f}"


def format_percentage(val: float, decimal_places: int = 2) -> str:
    """Formats a decimal or percentage number into a display string."""
    if pd.isna(val) or val is None:
        return "0.00%"
    return f"{val:.{decimal_places}f}%"


def execute_sql_file(con: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    """Executes all SQL statements in a given SQL file against the DuckDB connection."""
    if not sql_path.exists():
        logger.error(f"SQL file not found: {sql_path}")
        return
    logger.info(f"Executing SQL file: {sql_path.name}")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
    con.execute(sql_content)
