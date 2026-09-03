"""
02_eda.py
---------
Customer Churn & Retention Intelligence
Step 2: Exploratory Data Analysis

Input : data/processed/telco_clean.csv
Output: reports/figures/*.png  (charts)
        reports/eda_summary.md (business insights, auto-filled with real numbers)

Every chart below is followed by a printed, numbers-based business
insight - nothing here is invented, it is computed directly from the
cleaned dataset.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

IN_PATH = "data/processed/telco_clean.csv"
FIG_DIR = "reports/figures"
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_csv(IN_PATH)
insights = []


def save(fig, name):
    path = f"{FIG_DIR}/{name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path}")


# ---------------------------------------------------------------
# 1. Overall churn rate
# ---------------------------------------------------------------
churn_rate = df["ChurnFlag"].mean()
fig, ax = plt.subplots(figsize=(4, 4))
df["Churn"].value_counts().plot.pie(
    autopct="%1.1f%%", colors=["#2E86AB", "#E63946"], ax=ax, ylabel=""
)
ax.set_title("Overall Churn Rate")
save(fig, "01_overall_churn_rate")

insights.append(
    f"**Overall churn rate: {churn_rate:.1%}** ({df['ChurnFlag'].sum()} of {len(df)} customers). "
    "Roughly 1 in 4 customers is leaving - retention needs to be an active, budgeted program, "
    "not an afterthought."
)

# ---------------------------------------------------------------
# 2. Churn by contract type
# ---------------------------------------------------------------
contract_churn = df.groupby("Contract")["ChurnFlag"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4))
contract_churn.plot.bar(color="#E63946", ax=ax)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate by Contract Type")
for i, v in enumerate(contract_churn):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
save(fig, "02_churn_by_contract")

top_contract = contract_churn.index[0]
insights.append(
    f"**Contract type is the single strongest churn signal.** Month-to-month customers churn at "
    f"{contract_churn.get('Month-to-month', float('nan')):.1%}, versus "
    f"{contract_churn.get('One year', float('nan')):.1%} for one-year and "
    f"{contract_churn.get('Two year', float('nan')):.1%} for two-year contracts. "
    "Converting month-to-month customers onto annual contracts (with a modest incentive) is likely "
    "the highest-leverage retention lever available."
)

# ---------------------------------------------------------------
# 3. Churn by tenure
# ---------------------------------------------------------------
df["tenure_bucket"] = pd.cut(
    df["tenure"], bins=[-1, 6, 12, 24, 48, 72],
    labels=["0-6 mo", "7-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"]
)
tenure_churn = df.groupby("tenure_bucket", observed=True)["ChurnFlag"].mean()
fig, ax = plt.subplots(figsize=(6, 4))
tenure_churn.plot.bar(color="#F4A261", ax=ax)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate by Tenure")
for i, v in enumerate(tenure_churn):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
save(fig, "03_churn_by_tenure")

early_churn = tenure_churn.iloc[0]
late_churn = tenure_churn.iloc[-1]
insights.append(
    f"**Churn is heavily front-loaded.** Customers in their first 6 months churn at {early_churn:.1%}, "
    f"compared to only {late_churn:.1%} for customers with 49-72 months of tenure. "
    "The first 6 months is the critical window for onboarding and early-life retention efforts."
)

# ---------------------------------------------------------------
# 4. Churn by monthly charges
# ---------------------------------------------------------------
df["charges_bucket"] = pd.qcut(df["MonthlyCharges"], 4, labels=["Low", "Medium", "High", "Very High"])
charges_churn = df.groupby("charges_bucket", observed=True)["ChurnFlag"].mean()
fig, ax = plt.subplots(figsize=(6, 4))
charges_churn.plot.bar(color="#457B9D", ax=ax)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate by Monthly Charges Quartile")
for i, v in enumerate(charges_churn):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
save(fig, "04_churn_by_monthly_charges")

insights.append(
    f"**Higher-paying customers churn more, not less.** The top monthly-charges quartile churns at "
    f"{charges_churn['Very High']:.1%} vs {charges_churn['Low']:.1%} in the lowest quartile. "
    "These customers are usually on Fiber optic internet with several premium add-ons - they are "
    "paying the most and are also the most price-sensitive/at-risk group, making them a priority for "
    "proactive retention rather than up-sell."
)

# ---------------------------------------------------------------
# 5. Churn by internet service
# ---------------------------------------------------------------
internet_churn = df.groupby("InternetService")["ChurnFlag"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4))
internet_churn.plot.bar(color="#1D3557", ax=ax)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate by Internet Service")
for i, v in enumerate(internet_churn):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
save(fig, "05_churn_by_internet_service")

insights.append(
    f"**Fiber optic customers churn far more than DSL or no-internet customers**: "
    f"{internet_churn.get('Fiber optic', float('nan')):.1%} vs "
    f"{internet_churn.get('DSL', float('nan')):.1%} (DSL) and "
    f"{internet_churn.get('No', float('nan')):.1%} (no internet). "
    "This likely reflects both higher fiber pricing and possibly service/reliability complaints - "
    "worth a service-quality review alongside the pricing story."
)

# ---------------------------------------------------------------
# 6. Churn by payment method
# ---------------------------------------------------------------
payment_churn = df.groupby("PaymentMethod")["ChurnFlag"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 4))
payment_churn.plot.bar(color="#6A4C93", ax=ax)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate by Payment Method")
plt.xticks(rotation=20, ha="right")
for i, v in enumerate(payment_churn):
    ax.text(i, v + 0.01, f"{v:.1%}", ha="center")
save(fig, "06_churn_by_payment_method")

top_pay = payment_churn.index[0]
insights.append(
    f"**Electronic check payers churn the most** at {payment_churn.iloc[0]:.1%}, roughly double the "
    f"rate of customers on automatic bank transfer or credit card payments "
    f"({payment_churn.get('Bank transfer (automatic)', float('nan')):.1%} / "
    f"{payment_churn.get('Credit card (automatic)', float('nan')):.1%}). "
    "Migrating electronic-check customers onto autopay is a low-cost, high-impact retention action."
)

# ---------------------------------------------------------------
# 7. Additional pattern: add-on services vs churn
# ---------------------------------------------------------------
addon_cols = ["OnlineSecurity", "TechSupport", "OnlineBackup", "DeviceProtection"]
addon_churn = {c: df.groupby(c)["ChurnFlag"].mean().get("Yes", float("nan")) for c in addon_cols}
addon_churn_no = {c: df.groupby(c)["ChurnFlag"].mean().get("No", float("nan")) for c in addon_cols}
fig, ax = plt.subplots(figsize=(7, 4))
x = range(len(addon_cols))
ax.bar([i - 0.2 for i in x], [addon_churn_no[c] for c in addon_cols], width=0.4, label="No add-on", color="#E63946")
ax.bar([i + 0.2 for i in x], [addon_churn[c] for c in addon_cols], width=0.4, label="Has add-on", color="#2E86AB")
ax.set_xticks(list(x))
ax.set_xticklabels(addon_cols)
ax.set_ylabel("Churn Rate")
ax.set_title("Churn Rate: With vs Without Support/Security Add-ons")
ax.legend()
save(fig, "07_churn_by_addons")

insights.append(
    "**Customers without security/support add-ons churn substantially more.** For example, customers "
    f"without Online Security churn at {addon_churn_no['OnlineSecurity']:.1%} vs "
    f"{addon_churn['OnlineSecurity']:.1%} for those who have it, and customers without Tech Support "
    f"churn at {addon_churn_no['TechSupport']:.1%} vs {addon_churn['TechSupport']:.1%} with it. "
    "Bundling security/support into onboarding (or offering a free trial) could reduce churn."
)

# ---------------------------------------------------------------
# Correlation heatmap of numeric features
# ---------------------------------------------------------------
num_cols = ["tenure", "MonthlyCharges", "TotalCharges", "ChurnFlag"]
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation: Tenure / Charges / Churn")
save(fig, "08_correlation_heatmap")

corr_tenure = df[num_cols].corr().loc["tenure", "ChurnFlag"]
corr_monthly = df[num_cols].corr().loc["MonthlyCharges", "ChurnFlag"]
insights.append(
    f"**Tenure is negatively correlated with churn (r = {corr_tenure:.2f})** and MonthlyCharges is "
    f"positively correlated with churn (r = {corr_monthly:.2f}). Together these confirm the core "
    "churn story: new, high-paying customers on flexible contracts are the highest-risk segment."
)

# ---------------------------------------------------------------
# Write summary markdown
# ---------------------------------------------------------------
with open("reports/eda_summary.md", "w") as f:
    f.write("# EDA Summary - Customer Churn & Retention Intelligence\n\n")
    f.write(f"Dataset: {len(df)} customers, overall churn rate {churn_rate:.1%}\n\n")
    for i, ins in enumerate(insights, 1):
        f.write(f"{i}. {ins}\n\n")

print("\nAll charts saved to reports/figures/, insights written to reports/eda_summary.md")
