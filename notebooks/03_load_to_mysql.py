"""
03_load_to_mysql.py
--------------------
Loads the cleaned dataset (data/processed/telco_clean.csv) into the
MySQL/MariaDB `telco_churn.customers` table.

Requires: sql/01_schema.sql to have already been run, and a MySQL
server reachable with the credentials below.

Usage:
    python3 notebooks/03_load_to_mysql.py
"""

import pandas as pd
from sqlalchemy import create_engine

DB_USER = "churn_user"
DB_PASS = "churn_pass123"
DB_HOST = "localhost"
DB_NAME = "telco_churn"

CSV_PATH = "data/processed/telco_clean.csv"

def main():
    df = pd.read_csv(CSV_PATH)
    # Keep only the columns that exist in the SQL schema (drop the
    # helper bucket columns created for charting, if present).
    keep_cols = [
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
        "tenure", "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
        "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn", "ChurnFlag",
    ]
    df = df[keep_cols]

    engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
    df.to_sql("customers", engine, if_exists="append", index=False, method="multi", chunksize=500)

    with engine.connect() as conn:
        from sqlalchemy import text
        count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
    print(f"Loaded {count} rows into telco_churn.customers")


if __name__ == "__main__":
    main()
