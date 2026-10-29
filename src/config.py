"""Configuration loader and management module for collections forensics."""

import os
from pathlib import Path
from typing import Any, Dict
import yaml

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    return PROJECT_ROOT


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Loads and parses a YAML configuration file."""
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class Settings:
    """Central settings class providing typed access to project configuration."""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or (PROJECT_ROOT / "config")
        self.settings = load_yaml(self.config_dir / "settings.yaml")
        self.inventory = load_yaml(self.config_dir / "source_inventory.yaml")
        self.metrics = load_yaml(self.config_dir / "metric_definitions.yaml")

    @property
    def raw_data_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("raw_data_dir", "data/raw")

    @property
    def staging_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("staging_dir", "data/staging")

    @property
    def clean_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("clean_dir", "data/clean")

    @property
    def golden_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("golden_dir", "data/golden")

    @property
    def features_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("features_dir", "data/features")

    @property
    def duckdb_path(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("duckdb_database", "data/golden/collections_forensics.duckdb")

    @property
    def outputs_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("outputs_dir", "outputs")

    @property
    def sql_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("sql_dir", "sql")

    @property
    def reports_dir(self) -> Path:
        return PROJECT_ROOT / self.settings.get("paths", {}).get("reports_dir", "reports")

    @property
    def local_timezone(self) -> str:
        return self.settings.get("timezones", {}).get("business_local", "Asia/Kolkata")

    @property
    def attribution_window_days(self) -> int:
        return self.settings.get("forensic_rules", {}).get("attribution", {}).get("default_window_days", 14)

    @property
    def deduplication_window_seconds(self) -> int:
        return self.settings.get("forensic_rules", {}).get("deduplication", {}).get("payment_duplicate_window_seconds", 600)

    @property
    def capital_budget_inr(self) -> float:
        return float(self.settings.get("investment", {}).get("capital_budget_inr", 100000000.0))

    def get_source_spec(self, source_name: str) -> Dict[str, Any]:
        """Returns the schema specification for a given source dataset."""
        return self.inventory.get("sources", {}).get(source_name, {})


settings = Settings()
