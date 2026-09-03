"""
06_retention_priority.py
--------------------------
Customer Churn & Retention Intelligence
Step 6: Retention Priority

Combines:
    - Churn Probability (from the Random Forest model, step 5)
    - Customer Value (TotalCharges - what they've actually spent so far,
      the cleanest "value" measure we have without inventing a CLV formula)

into a 2x2 priority matrix, using the dataset's own median as the
value cutoff and 0.5 as the churn-risk cutoff (a customer the model
thinks is more likely than not to churn is "high risk").

Priority groups
-----------------
| Customer Type                   | Priority             |
|----------------------------------|----------------------|
| High Value + High Churn Risk     | Critical             |
| Medium Value + High Churn Risk   | High                 |  (kept as
                                                              a 3-value
                                                              split below
                                                              for realism)
| Low Value + High Churn Risk      | Low-Cost Retention   |
| High Value + Low Churn Risk      | Maintain             |

To make the "Medium Value" tier meaningful (the brief's table implies
3 value tiers, not 2), value is split into 3 tiers (Low / Medium / High)
using terciles of TotalCharges, while risk stays a simple High/Low split
at the 0.5 probability threshold. This keeps the logic simple and fully
explainable while matching the requested table exactly.

Output:
    - data/processed/telco_retention_priority.csv
    - reports/retention_priority_summary.md
"""

import pandas as pd

IN_PATH = "data/processed/telco_scored.csv"
OUT_PATH = "data/processed/telco_retention_priority.csv"

df = pd.read_csv(IN_PATH)

# --- Value tiers: terciles of TotalCharges (grounded in real data) ---
df["ValueTercile"] = pd.qcut(df["TotalCharges"], 3, labels=["Low Value", "Medium Value", "High Value"])

# --- Risk tier: model says more-likely-than-not to churn ---
RISK_THRESHOLD = 0.5
df["RiskTier"] = df["ChurnProbability"].apply(lambda p: "High Risk" if p >= RISK_THRESHOLD else "Low Risk")


def assign_priority(row):
    v, r = row["ValueTercile"], row["RiskTier"]
    if r == "High Risk" and v == "High Value":
        return "Critical"
    elif r == "High Risk" and v == "Medium Value":
        return "High"
    elif r == "High Risk" and v == "Low Value":
        return "Low-Cost Retention"
    elif r == "Low Risk" and v == "High Value":
        return "Maintain"
    elif r == "Low Risk" and v == "Medium Value":
        return "Monitor"
    else:  # Low Risk + Low Value
        return "No Action Needed"


df["RetentionPriority"] = df.apply(assign_priority, axis=1)

RECOMMENDATIONS = {
    "Critical": "Immediate, high-touch outreach (dedicated retention agent or account call). "
                "Offer a loyalty discount or contract upgrade incentive - these are the customers "
                "who cost the most to lose.",
    "High": "Proactive outreach via email/call campaign with a targeted offer (e.g. contract "
            "upgrade discount, free add-on trial). Automate where possible to manage cost.",
    "Low-Cost Retention": "Low-cost, automated retention: email nudges, self-serve loyalty "
                           "discounts, or migration to autopay. Not worth expensive white-glove "
                           "outreach given their spend level.",
    "Maintain": "No urgent action - maintain service quality and continue standard engagement "
                "(newsletters, loyalty perks) to protect this already-stable, valuable relationship.",
    "Monitor": "No immediate action, but include in periodic risk re-scoring - keep an eye out for "
               "any drop in engagement or a support complaint that could push them into a higher-risk tier.",
    "No Action Needed": "Minimal investment - standard service only. Revisit if their spend or "
                         "risk profile changes.",
}
df["RecommendedAction"] = df["RetentionPriority"].map(RECOMMENDATIONS)

df.to_csv(OUT_PATH, index=False)

# ---------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------
summary = df.groupby("RetentionPriority").agg(
    customers=("customerID", "count"),
    avg_churn_probability=("ChurnProbability", "mean"),
    avg_total_charges=("TotalCharges", "mean"),
    monthly_revenue_at_risk=("MonthlyCharges", lambda s: s[df.loc[s.index, "RiskTier"] == "High Risk"].sum()),
).round(2)

order = ["Critical", "High", "Low-Cost Retention", "Maintain", "Monitor", "No Action Needed"]
summary = summary.reindex([o for o in order if o in summary.index])

print("--- Retention Priority Summary ---")
print(summary)

total_at_risk_customers = (df["RiskTier"] == "High Risk").sum()
total_monthly_revenue_at_risk = df.loc[df["RiskTier"] == "High Risk", "MonthlyCharges"].sum()
critical_count = (df["RetentionPriority"] == "Critical").sum()
critical_revenue = df.loc[df["RetentionPriority"] == "Critical", "MonthlyCharges"].sum()

report_lines = [
    "# Retention Priority Summary\n",
    f"Total customers flagged High Risk (model probability >= {RISK_THRESHOLD}): "
    f"**{total_at_risk_customers}** ({total_at_risk_customers/len(df):.1%} of the customer base)\n",
    f"Total monthly revenue at risk from these customers: **${total_monthly_revenue_at_risk:,.2f}/month** "
    f"(~${total_monthly_revenue_at_risk*12:,.0f}/year if all churned)\n",
    f"**Critical priority customers: {critical_count}**, representing "
    f"${critical_revenue:,.2f}/month of revenue - these are high-value, high-risk customers "
    "who should be the very first call list for the retention team.\n",
    "## Priority Group Breakdown\n",
    "| Priority | Customers | Avg Churn Probability | Avg Total Charges ($) | Monthly Revenue at Risk ($) |",
    "|---|---|---|---|---|",
]
for priority in order:
    if priority in summary.index:
        row = summary.loc[priority]
        report_lines.append(
            f"| {priority} | {int(row['customers'])} | {row['avg_churn_probability']:.2f} | "
            f"{row['avg_total_charges']:,.2f} | {row['monthly_revenue_at_risk']:,.2f} |"
        )

report_lines.append("\n## Recommended Action per Priority Group\n")
for priority in order:
    if priority in df["RetentionPriority"].unique():
        report_lines.append(f"**{priority}**: {RECOMMENDATIONS[priority]}\n")

with open("reports/retention_priority_summary.md", "w") as f:
    f.write("\n".join(report_lines))

print(f"\nSaved {OUT_PATH} and reports/retention_priority_summary.md")
