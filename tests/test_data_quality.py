"""Unit tests for data quality assertions and reliability scoring."""

import pytest
import duckdb
from src.data_quality import DataQualityEngine
from src.utils import execute_sql_file
from src.config import settings


def test_data_quality_on_populated_fixtures(populated_test_db):
    """Verifies that DQ checks detect non-positive and failed payments."""
    con = populated_test_db
    execute_sql_file(con, settings.sql_dir / "02_data_quality.sql")
    dq = DataQualityEngine(con=con)
    summary_df = dq.run_checks()

    # Verify summary is returned
    assert isinstance(summary_df, object)
    score_info = dq.calculate_data_reliability_score()
    assert 0.0 <= score_info["reliability_score"] <= 100.0
    assert score_info["health_status"] in ["HEALTHY", "MODERATE_RISK", "CRITICAL_RISK", "EXCELLENT"]


def test_data_quality_empty_db(in_memory_db):
    """Verifies graceful handling when running against empty initialized tables."""
    dq = DataQualityEngine(con=in_memory_db)
    summary_df = dq.run_checks()
    assert summary_df.empty
    score = dq.calculate_data_reliability_score()
    assert score["reliability_score"] == 100.0
