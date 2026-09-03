"""
run_pipeline.py
-----------------
Runs the full Customer Churn & Retention Intelligence pipeline end-to-end,
in order. Assumes:
    - data/raw/Telco-Customer-Churn.csv already exists
    - requirements.txt has been installed
    - (optional) MySQL/MariaDB is running locally if you want the SQL step -
      the ML pipeline itself does not depend on the database.

Usage:
    python run_pipeline.py            # runs everything except the MySQL load
    python run_pipeline.py --with-sql # also loads into MySQL (requires a running server)
"""
import subprocess
import sys

STEPS = [
    "notebooks/01_data_cleaning.py",
    "notebooks/02_eda.py",
    "notebooks/04_customer_segmentation.py",
    "notebooks/05_churn_prediction.py",
    "notebooks/06_retention_priority.py",
]

SQL_STEP = "notebooks/03_load_to_mysql.py"


def run(script):
    print(f"\n{'='*70}\nRunning {script}\n{'='*70}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Step failed: {script}")
        sys.exit(1)


if __name__ == "__main__":
    if "--with-sql" in sys.argv:
        STEPS.insert(2, SQL_STEP)  # after cleaning + EDA, before segmentation

    for step in STEPS:
        run(step)

    print("\nPipeline complete. See reports/ for outputs, data/processed/ for datasets.")
