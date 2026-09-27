# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-27

### Added
- **Official Pokémon Database Dataset** (`data/pokemon_database_raw.csv`, `data/Pokemon Dataset - Sheet1.csv`): Official 1,220-row database of all nine Pokémon generations scraped from the Pokémon Database (PokéBase).
- **Cleaned Dataset & Engineered Features** (`data/pokemon_database_cleaned.csv`): Clean 1,219-row dataset with engineered combat metrics: `Avg_Stats`, `Physical_Power`, `Special_Power`, `Offensive_Power`, `Defensive_Power`, `Primary_Type`, `Secondary_Type`, and `Power_Category` ('Weak', 'Average', 'Strong', 'Legendary').
- **Working Paper & Term Paper Artifacts**:
  - `output/Pokemon_Type_and_Battle_Role_Term_Paper.pdf`: Complete 28-page official academic term paper submission.
  - `output/Pokemon_Type_and_Battle_Role_Term_Paper.docx`: Publication-grade formatted Word document with all tables, headings, and figures embedded.
  - `output/Pokemon_Type_and_Battle_Role_Term_Paper_generated.pdf`: PDF compiled directly from the Word document.
- **Reproducible Python Data Science Pipeline** (`scripts/`):
  - `build_analysis_data.py`: Ingestion, data cleaning, statistical modeling, ANOVA, t-tests, K-Means clustering, and JSON export.
  - `make_charts.py`: Publication-grade rendering of all 10 analytical figures in PNG (300 DPI) and vector PDF.
  - `verified_charts.py`: Verified academic serif figure generation with Cambria typography and standardized institutional footers.
  - `build_report.py`: Word document compiler utilizing `python-docx` with Word COM PDF conversion.
  - `report_reconciliation.py`: Mathematical audit script reconciling raw data, code calculations, and paper claims.
  - `verify_report.py`: Automated test suite executing 128 assertion checks ensuring 100% empirical reproducibility.
  - `generate_notebook.py`: Script to generate the interactive Jupyter notebook.
- **Interactive Jupyter Research Notebook** (`notebooks/pokemon_battle_role_analysis.ipynb`): End-to-end executable notebook detailing every methodology phase with visualizations and markdown narratives.
- **Documentation Suite** (`docs/`):
  - `data-replication-guide.md`: Provenance, scraping details, cleaning steps, and 1-click replication runbook.
  - `statistical-methodology.md`: Mathematical derivations for ANOVA, t-tests, Pearson/Spearman correlations, and K-Means clustering.
  - `project-context.md`: CSD105 course background, team member attributions, and academic scope.
- **GitHub Workflow & Issue Templates** (`.github/ISSUE_TEMPLATE/`):
  - `bug_report.yml`: Standardized template for code, script, or environment bugs.
  - `replication_inquiry.yml`: Standardized template for statistical replication questions.
- **Licensing & Community Standards**:
  - `LICENSE-CODE`: MIT License for all computational code and pipeline scripts.
  - `LICENSE-DOCS`: Creative Commons Attribution 4.0 International (CC-BY-4.0) for paper text, figures, and documentation.
  - `CONTRIBUTING.md`: Contribution standards and code of conduct.
  - `README.md`: Flagship presentation repository documentation with executive findings, data tables, inline figure previews, and BibTeX citations.
