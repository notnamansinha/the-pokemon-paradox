# Contributing

This repository archives an academic data science term paper and empirical research pipeline completed for course **CSD105 – Introduction to Data Science** at Ahmedabad University.

The analytical pipeline, charts, statistical models, and working paper are published for transparency, educational utility, and full scientific reproducibility.

## Reporting Issues

Please open an issue if you encounter:

- A discrepancy in statistical outputs, p-values, or correlation coefficients.
- A bug or syntax error in any Python script or notebook.
- Environment incompatibility or missing package dependency.
- Data formatting inconsistencies.

## Pull Requests

Pull requests that enhance script portability, improve visualization accessibility, optimize performance, or add supplementary analysis are welcome. Modifications to core statistical results or conclusions require documented justification and accompanying test updates in `scripts/verify_report.py`.

## Code Style

- Python scripts strictly adhere to **PEP 8**.
- Markdown documentation uses standard ATX headings (`#`), GitHub-flavored tables, and relative markdown links.
- Automated tests in `scripts/verify_report.py` must pass with 0 failures prior to submitting any PR.

## License

By contributing, you agree that your contributions are licensed under the **MIT License** (for code artifacts) and **Creative Commons Attribution 4.0 International (CC-BY-4.0)** (for documentation and papers), consistent with repository license files.
