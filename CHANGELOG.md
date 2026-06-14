# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.0] — 2025-XX-XX

### Added
- Initial dataset: 1,000 IMDb top-rated films scored across 20+ experiential dimensions
- `data_dictionary.csv` — full schema documentation with column types, value ranges, and descriptions
- `generate_profiles.py` — LLM pipeline using Gemini 2.5 Flash with Pydantic schema enforcement, incremental writes, and 429 retry logic
- `run_profiler_loop.sh` — multi-key orchestration script for unattended free-tier runs
- `cinatomy_analysis.ipynb` — EDA notebook covering feature importance analysis, K-Means experiential clustering, and radar chart comparisons
- Kaggle dataset published with usability score 10
