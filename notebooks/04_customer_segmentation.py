"""
04_customer_segmentation.py
----------------------------
Customer Churn & Retention Intelligence
Step 4: Customer Segmentation

Creates simple, explainable rule-based segments using tenure,
MonthlyCharges and TotalCharges - no clustering black-box, so anyone
in the business can understand exactly why a customer landed in a
given segment.

Segmentation logic
-------------------
Step 1 - Tenure stage:
    New          : tenure <= 12 months
    Growing      : 12 < tenure <= 36 months
    Loyal        : tenure > 36 months

Step 2 - Value tier (based on TotalCharges, using the dataset's own
    quartiles so the thresholds are grounded in the actual data,
    not arbitrary round numbers):
    Low value    : bottom 50% of TotalCharges
    High value   : top 50% of TotalCharges

Combining the two gives 6 human-readable segments, e.g.
"New - Low Value", "Loyal - High Value", etc. We then map these to
the four example buckets requested (New / Growing / Loyal / High-Value)
by taking the tenure stage as the primary label and calling out the
high-value cross-cut separately - this keeps the story simple while
still preserving the value dimension for the retention-priority step.

Output: data/processed/telco_segmented.csv
"""

import pandas as pd

IN_PATH = "data/processed/telco_clean.csv"
OUT_PATH = "data/processed/telco_segmented.csv"

df = pd.read_csv(IN_PATH)


def tenure_stage(t):
    if t <= 12:
        return "New Customer"
    elif t <= 36:
        return "Growing Customer"
    else:
        return "Loyal Customer"


df["TenureSegment"] = df["tenure"].apply(tenure_stage)

value_median = df["TotalCharges"].median()
df["ValueTier"] = df["TotalCharges"].apply(lambda x: "High Value" if x >= value_median else "Low Value")

# Combined, business-readable segment label
df["CustomerSegment"] = df["TenureSegment"] + " - " + df["ValueTier"]

# A simplified single label matching the four example buckets in the
# brief: any High Value customer who is also Loyal gets called out
# explicitly as "High-Value Customer" since that is the group the
# business cares most about protecting.
def simple_segment(row):
    if row["TenureSegment"] == "Loyal Customer" and row["ValueTier"] == "High Value":
        return "High-Value Customer"
    return row["TenureSegment"]


df["SimpleSegment"] = df.apply(simple_segment, axis=1)

print("Median TotalCharges used as value cutoff: ${:.2f}".format(value_median))
print("\n--- Segment sizes (SimpleSegment) ---")
print(df["SimpleSegment"].value_counts())

print("\n--- Churn rate & profile by SimpleSegment ---")
summary = df.groupby("SimpleSegment").agg(
    customers=("customerID", "count"),
    avg_tenure=("tenure", "mean"),
    avg_monthly_charges=("MonthlyCharges", "mean"),
    avg_total_charges=("TotalCharges", "mean"),
    churn_rate=("ChurnFlag", "mean"),
).round(2).sort_values("churn_rate", ascending=False)
print(summary)

print("\n--- Full 6-way CustomerSegment cross-tab ---")
cross = df.groupby("CustomerSegment").agg(
    customers=("customerID", "count"),
    churn_rate=("ChurnFlag", "mean"),
).round(3).sort_values("churn_rate", ascending=False)
print(cross)

df.to_csv(OUT_PATH, index=False)
print(f"\nSaved segmented dataset -> {OUT_PATH}")
