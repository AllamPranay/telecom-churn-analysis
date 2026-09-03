# Power BI Dashboard - Build Guide

This project ships the **data**, not a binary `.pbix` file, because `.pbix` files are
Power BI Desktop's proprietary binary format and can't be generated outside the actual
application. Everything below is copy-paste ready: load the CSV, paste in the DAX
measures, and follow the page layout - it will take about 20-30 minutes to build.

## 1. Data source

Load **`powerbi/telco_powerbi_dataset.csv`** into Power BI (`Get Data > Text/CSV`).
This is the fully-scored dataset (7,043 rows) - it already contains the cleaned fields,
the ML churn probability, and the retention priority label, so no additional
transformation is required in Power Query beyond setting correct data types:

| Column | Type |
|---|---|
| tenure, SeniorCitizen (if using 0/1) | Whole Number |
| MonthlyCharges, TotalCharges, ChurnProbability | Decimal Number |
| ChurnFlag | Whole Number |
| Everything else | Text |

## 2. Key DAX measures

Create these as new measures (Modeling > New Measure) on the `telco_powerbi_dataset` table:

```dax
Total Customers = COUNTROWS(telco_powerbi_dataset)

Churned Customers = CALCULATE([Total Customers], telco_powerbi_dataset[Churn] = "Yes")

Churn Rate = DIVIDE([Churned Customers], [Total Customers], 0)

High Risk Customers =
CALCULATE([Total Customers], telco_powerbi_dataset[RiskTier] = "High Risk")

Critical Priority Customers =
CALCULATE([Total Customers], telco_powerbi_dataset[RetentionPriority] = "Critical")

Monthly Revenue at Risk =
CALCULATE(
    SUM(telco_powerbi_dataset[MonthlyCharges]),
    telco_powerbi_dataset[RiskTier] = "High Risk"
)

Annual Revenue at Risk = [Monthly Revenue at Risk] * 12

Avg Churn Probability = AVERAGE(telco_powerbi_dataset[ChurnProbability])

Total Monthly Revenue = SUM(telco_powerbi_dataset[MonthlyCharges])
```

## 3. Page 1 - Executive Overview

**Layout:** 4 KPI cards across the top, one chart below.

| Visual | Field(s) |
|---|---|
| Card | `[Total Customers]` |
| Card | `[Churn Rate]` (format as %) |
| Card | `[High Risk Customers]` |
| Card | `[Monthly Revenue at Risk]` (format as currency) |
| Donut chart | `Churn` (legend) x `[Total Customers]` (values) - overall churn split |
| Bar chart | `RetentionPriority` (axis) x `[Total Customers]` (values) - customers per priority tier |

**Business framing for the page header:** *"26.5% of our ~7,000 customers have
churned historically, and the model currently flags ~39% of the active base as
high-risk, representing over $200K/month of revenue exposure."* (Numbers pull live
from the measures above, so update the text box if the data changes.)

## 4. Page 2 - Churn Analysis

**Layout:** 2x2 grid of charts + one KPI strip.

| Visual | Field(s) |
|---|---|
| Clustered bar | `Contract` (axis) x `[Churn Rate]` (values) |
| Line/bar | `tenure` (axis, binned every 6 months via "New group") x `[Churn Rate]` |
| Clustered bar | `InternetService` (axis) x `[Churn Rate]` |
| Clustered bar | `PaymentMethod` (axis) x `[Churn Rate]` |
| Table or key influencers visual | Use Power BI's built-in **Key Influencers** visual with
  `Churn` as the field to analyze - it will automatically surface Contract, tenure,
  InternetService, and PaymentMethod as top drivers, matching the Python model's findings. |

Add a slicer for `Contract` and `InternetService` so the whole page can be filtered
interactively.

## 5. Page 3 - Retention Strategy

**Layout:** scatter plot as the centerpiece, table + recommendations alongside.

| Visual | Field(s) |
|---|---|
| Scatter chart | X = `TotalCharges`, Y = `ChurnProbability`, Legend = `RetentionPriority`, Size = `MonthlyCharges` - this recreates `reports/figures/14_value_vs_risk_scatter.png` interactively |
| Table | `customerID`, `TotalCharges`, `ChurnProbability`, `RetentionPriority`, `RecommendedAction`, filtered to `RetentionPriority = "Critical"`, sorted by `TotalCharges` descending - this is the retention team's literal call list |
| Card strip | `[Critical Priority Customers]`, and a measure `Critical Revenue = CALCULATE(SUM(MonthlyCharges), RetentionPriority="Critical")` |
| Slicer | `RetentionPriority` so a rep can click "Critical" and see just that list |

## 6. Suggested visual theme

Use a simple 3-color palette matching the Python charts for consistency across the
whole project: `#E63946` (risk/red), `#2E86AB` (neutral/blue), `#2A9D8F` (safe/green).
Apply it via View > Themes > Customize current theme.

## 7. Files in this folder

- `telco_powerbi_dataset.csv` - the single flat table to import (source of truth for all 3 pages)
- This guide (`README.md` in this folder)
