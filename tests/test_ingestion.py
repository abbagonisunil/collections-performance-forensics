"""Unit tests for ingestion engine and schema initialization."""

import pytest
import duckdb
from src.ingestion import IngestionEngine, EXPECTED_SOURCES


def test_discovery_handles_empty_raw_directory(tmp_path, in_memory_db):
    """Verifies that an empty raw folder is gracefully identified as AWAITING_DATA."""
    engine = IngestionEngine(raw_dir=tmp_path, con=in_memory_db)
    discovery = engine.discover_raw_files()
    assert len(discovery) == len(EXPECTED_SOURCES)
    for src in EXPECTED_SOURCES:
        assert discovery[src]["status"] == "AWAITING_DATA"
        assert discovery[src]["file_path"] is None


def test_initialize_empty_schemas(in_memory_db):
    """Verifies that all 17 raw tables can be initialized with typed schemas."""
    engine = IngestionEngine(con=in_memory_db)
    for src in EXPECTED_SOURCES:
        engine.initialize_empty_schema(src)
        # Check table exists in DuckDB
        res = in_memory_db.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'raw_{src}';").fetchone()
        assert res[0] == 1
