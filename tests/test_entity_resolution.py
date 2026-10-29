"""Unit tests for entity resolution and telephony disposition mapping."""

import pytest
import duckdb
from src.entity_resolution import EntityResolver


def test_entity_resolution_crosswalks(populated_test_db):
    """Verifies that crosswalks resolve disposition codes and link accounts."""
    con = populated_test_db
    resolver = EntityResolver(con=con)
    stats = resolver.build_crosswalks()

    assert "ref_disposition_crosswalk" in stats

    # Verify RPC_PTP maps to canonical RPC
    disp_map = dict(con.execute("SELECT disposition_code_raw, canonical_disposition_category FROM ref_disposition_crosswalk;").fetchall())
    assert disp_map.get("RPC_PTP") == "RPC"
    assert disp_map.get("RPC_CALL_BACK") == "RPC"
