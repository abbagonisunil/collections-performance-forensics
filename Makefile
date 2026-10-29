# Collections Performance Forensics - Makefile
# Reproducible execution commands for pipeline, testing, and dashboard

.PHONY: help setup profile pipeline notebook-check test dashboard all clean

PYTHON = python3
PIP = pip

help:
	@echo "Collections Performance Forensics - Available Commands:"
	@echo "  make setup          - Install dependencies from requirements.txt"
	@echo "  make profile        - Discover and profile all 17 raw collection sources"
	@echo "  make pipeline       - Execute full forensic pipeline & DuckDB golden dataset build"
	@echo "  make test           - Run automated pytest unit test suite"
	@echo "  make notebook-check - Validate complete 24-section investigation notebook"
	@echo "  make dashboard      - Launch Streamlit executive leadership dashboard"
	@echo "  make all            - Run profile, pipeline, test, and notebook-check in sequence"
	@echo "  make clean          - Remove caches, temporary databases, and execution logs"

setup:
	$(PIP) install -r requirements.txt

profile:
	$(PYTHON) -c "from src.profiling import profile_sources; print(profile_sources())"

pipeline:
	$(PYTHON) -m src.pipeline

test:
	$(PYTHON) -m pytest -v tests/

notebook-check:
	jupyter nbconvert --to notebook --execute notebooks/01_collections_performance_investigation.ipynb --output test_executed.ipynb && rm -f test_executed.ipynb

dashboard:
	streamlit run dashboard/app.py

all: profile pipeline test notebook-check
	@echo "=== All forensic stages, pipelines, and validation tests passed successfully! ==="

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	rm -f data/golden/*.duckdb.wal test_executed.ipynb
