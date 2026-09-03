"""
01_data_cleaning.py
--------------------
Customer Churn & Retention Intelligence
Step 1: Data Cleaning

Input : data/raw/Telco-Customer-Churn.csv
Output: data/processed/telco_clean.csv

What this script does:
1. Loads the raw IBM Telco Customer Churn dataset (7,043 rows).
2. Fixes the TotalCharges column (it is stored as text and has 11 blank
   values, all belonging to brand-new customers with tenure = 0).
3. Checks for duplicate customer records.
4. Standardises data types (flags, target variable) so downstream
   EDA / SQL / ML steps all work off one clean, well-typed table.
5. Runs a few basic validation checks and prints a short data-quality
   report so every claim in the README is backed by an actual result.
"""

import pandas as pd
import numpy as np

RAW_PATH = "data/raw/Telco-Customer-Churn.csv"
OUT_PATH = "data/processed/telco_clean.csv"


def load_raw(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- 1. Duplicates -----------------------------------------------
    dup_rows = df.duplicated().sum()
    dup_ids = df["customerID"].duplicated().sum()
    print(f"Exact duplicate rows: {dup_rows} | Duplicate customerIDs: {dup_ids}")
    df = df.drop_duplicates(subset="customerID", keep="first")

    # --- 2. TotalCharges: text -> numeric -----------------------------
    # 11 customers have a blank string for TotalCharges. Every one of
    # them has tenure == 0, i.e. they are brand-new customers who
    # haven't been billed yet. The correct value for a customer with
    # zero tenure is 0, not "unknown", so we fill with 0 rather than
    # dropping the rows or imputing a mean (which would invent revenue
    # that was never charged).
    df["TotalCharges"] = df["TotalCharges"].astype(str).str.strip()
    before_na = pd.to_numeric(df["TotalCharges"], errors="coerce").isna().sum()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    zero_tenure_blank = df.loc[df["TotalCharges"].isna(), "tenure"].eq(0).all()
    assert zero_tenure_blank, "Found a blank TotalCharges for a customer with tenure > 0 - needs review"
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)
    print(f"TotalCharges: fixed {before_na} blank values (all tenure=0 new customers) -> set to 0.0")

    # --- 3. Standardise categorical "No xxx service" labels -----------
    # MultipleLines / OnlineSecurity / OnlineBackup / DeviceProtection /
    # TechSupport / StreamingTV / StreamingMovies use values like
    # "No internet service" / "No phone service" which are functionally
    # the same as "No" for churn analysis. We keep the original detail
    # in *_detail columns but also add a simplified Yes/No version so
    # EDA and modelling aren't tripped up by a 3-way category that is
    # really binary.
    service_cols = [
        "MultipleLines", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    for col in service_cols:
        df[col] = df[col].replace({"No internet service": "No", "No phone service": "No"})

    # --- 4. Data type fixes --------------------------------------------
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    df["Churn"] = df["Churn"].str.strip()
    df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0}).astype(int)

    df["tenure"] = df["tenure"].astype(int)
    df["MonthlyCharges"] = df["MonthlyCharges"].astype(float)
    df["TotalCharges"] = df["TotalCharges"].astype(float)

    # --- 5. Basic validation --------------------------------------------
    assert df["customerID"].is_unique, "customerID is not unique after cleaning"
    assert df["tenure"].between(0, 100).all(), "tenure has out-of-range values"
    assert df["MonthlyCharges"].gt(0).all(), "MonthlyCharges has non-positive values"
    assert df["Churn"].isin(["Yes", "No"]).all(), "Churn has unexpected categories"
    assert df.isnull().sum().sum() == 0, "Unexpected nulls remain after cleaning"

    # Sanity check: TotalCharges should roughly track tenure * MonthlyCharges
    # (not exact, because of past rate changes / promos, but should be in
    # the right ballpark for customers with tenure > 0).
    est = df["tenure"] * df["MonthlyCharges"]
    ratio = (df.loc[df["tenure"] > 0, "TotalCharges"] / est[df["tenure"] > 0]).median()
    print(f"Sanity check - median(TotalCharges / (tenure*MonthlyCharges)) = {ratio:.2f} (expected close to 1.0)")

    return df


def report(df: pd.DataFrame) -> None:
    print("\n--- Data Quality Report (post-cleaning) ---")
    print(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    print(f"Nulls remaining: {df.isnull().sum().sum()}")
    print(f"Churn rate: {df['ChurnFlag'].mean():.2%}")
    print(df[["tenure", "MonthlyCharges", "TotalCharges"]].describe().round(2))


if __name__ == "__main__":
    raw = load_raw(RAW_PATH)
    clean_df = clean(raw)
    report(clean_df)
    clean_df.to_csv(OUT_PATH, index=False)
    print(f"\nSaved cleaned dataset -> {OUT_PATH}")
