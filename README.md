# Telecom Churn Driver Analysis

**Role framing:** Data Analyst at a telecom company that is losing customers and has
limited retention resources - the goal is not just to predict churn, but to tell the
business *who* to save and *what* to do about it.

> I analyzed customer churn in a telecom company, identified the major factors
> associated with churn, built machine learning models to predict churn risk,
> combined churn probability with customer value, and created a retention
> prioritization strategy to help the business focus its retention efforts.

Dataset: **IBM Telco Customer Churn** (7,043 customers, 21 original columns).
Target: the existing `Churn` column (Yes/No).

---

## Business questions this project answers

1. **Which customers are likely to churn?** → `models/random_forest.pkl` scores every
   customer with a churn probability (`ChurnProbability` column).
2. **What factors are associated with churn?** → `reports/eda_summary.md` +
   `reports/model_comparison.md` (contract type, tenure, internet service, payment
   method, and monthly charges are the dominant drivers).
3. **Which customers are most valuable and at risk?** → `reports/figures/14_value_vs_risk_scatter.png`
   plots every customer by value (`TotalCharges`) vs risk (`ChurnProbability`).
4. **Which customers should be prioritized for retention?** → `reports/retention_priority_summary.md`
   ranks customers into Critical / High / Low-Cost Retention / Maintain / Monitor / No Action Needed.
5. **What business action should be recommended?** → each priority tier has a concrete,
   costed recommendation (see section 6 below and the Power BI Page 3).

---

## Key results (real numbers from this run - see `reports/` for full detail)

| Metric | Value |
|---|---|
| Overall churn rate | **26.5%** (1,869 of 7,043 customers) |
| Month-to-month contract churn rate | **42.7%** vs 11.3% (1-yr) / 2.8% (2-yr) |
| First-6-months churn rate | **52.9%** vs 9.5% for 49-72 month tenure |
| Fiber optic churn rate | **41.9%** vs 19.0% (DSL) / 7.4% (no internet) |
| Electronic check churn rate | **45.3%** vs ~15-17% for autopay methods |
| Best model (Random Forest) ROC-AUC | **0.848** (Logistic Regression: 0.842) |
| Random Forest recall on churners | **79.4%** at 52.8% precision |
| Customers flagged High Risk (P ≥ 0.5) | **2,769** (39.3% of base) |
| Monthly revenue at risk | **$206,607** (~$2.48M/year if all high-risk churned) |
| **Critical priority customers** (high value + high risk) | **491**, $47,233/month |

---

## Project structure

```
churn_project/
├── data/
│   ├── raw/Telco-Customer-Churn.csv          # original IBM dataset (7,043 rows)
│   └── processed/                             # output of each pipeline stage
│       ├── telco_clean.csv                    # after Step 1 cleaning
│       ├── telco_segmented.csv                # after Step 4 segmentation
│       ├── telco_scored.csv                   # after Step 5 (+ ChurnProbability)
│       └── telco_retention_priority.csv       # after Step 6 (final, richest table)
├── notebooks/                                  # run in this order
│   ├── 01_data_cleaning.py
│   ├── 02_eda.py
│   ├── 03_load_to_mysql.py                     # optional, needs a running MySQL server
│   ├── 04_customer_segmentation.py
│   ├── 05_churn_prediction.py
│   └── 06_retention_priority.py
├── sql/
│   ├── 01_schema.sql                           # database + table + indexes
│   ├── 02_analysis_queries.sql                 # all analysis queries (GROUP BY, CASE, CTEs, window fns)
│   └── results/query_results.md                # actual output of every query, for reference
├── models/
│   ├── logistic_regression.pkl
│   └── random_forest.pkl
├── reports/
│   ├── eda_summary.md                          # 8 numbered, numbers-backed business insights
│   ├── model_comparison.md                     # metrics, confusion matrices, business interpretation
│   ├── retention_priority_summary.md           # priority tiers + recommended actions
│   └── figures/                                # 14 charts (churn drivers, ROC curve, confusion matrices, etc.)
├── powerbi/
│   ├── telco_powerbi_dataset.csv               # single flat table for Power BI import
│   └── README.md                               # step-by-step dashboard build guide with DAX measures
├── requirements.txt
├── run_pipeline.py                             # runs the whole thing end-to-end
└── README.md                                   # this file
```

---

## How to reproduce this project

```bash
# 1. Set up environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Run the full pipeline (cleaning -> EDA -> segmentation -> ML -> retention priority)
python run_pipeline.py

# 3. (Optional) Load into MySQL and run the SQL analysis
#    - start a local MySQL/MariaDB server first
mysql -u root < sql/01_schema.sql
python notebooks/03_load_to_mysql.py
mysql -u root telco_churn < sql/02_analysis_queries.sql

# 4. Open Power BI Desktop and import powerbi/telco_powerbi_dataset.csv
#    - follow powerbi/README.md for the exact DAX measures and page layout
```

---

## 1. Data Cleaning (`notebooks/01_data_cleaning.py`)

- **TotalCharges** was stored as text with 11 blank values - every one of them belongs
  to a customer with `tenure = 0` (brand-new, not yet billed), so they were filled with
  `0.0` rather than dropped or mean-imputed (which would have invented revenue that was
  never actually charged).
- **Duplicates:** none found (`customerID` is already unique).
- Standardised "No internet service" / "No phone service" labels down to "No" for the
  add-on columns (they are functionally equivalent to "No" for churn analysis).
- Converted `SeniorCitizen` (0/1) to Yes/No for readability and added a numeric
  `ChurnFlag` (0/1) alongside the original `Churn` (Yes/No) text column.
- Ran basic validation: uniqueness, value ranges, no unexpected nulls, and a sanity
  check that `TotalCharges ≈ tenure × MonthlyCharges` (median ratio = 1.00 ✓).

## 2. Exploratory Data Analysis (`notebooks/02_eda.py`)

8 charts, each paired with a numbers-backed business insight in `reports/eda_summary.md`:
overall churn rate, churn by contract, churn by tenure, churn by monthly charges, churn
by internet service, churn by payment method, churn by add-on services, and a
correlation heatmap. Headline finding: **new, high-paying, month-to-month customers on
Fiber optic paying by electronic check are the highest-risk segment** - this single
sentence is corroborated independently by the EDA, the SQL segment query, and the
Random Forest feature importances below.

## 3. SQL Analysis (`sql/`)

The cleaned dataset is loaded into a MySQL/MariaDB `telco_churn.customers` table.
`sql/02_analysis_queries.sql` covers every requested pattern:
- **GROUP BY + CASE**: churn rate by contract, internet service, payment method
- **CTE + NTILE() window function**: customers split into value quartiles, with churn
  rate and revenue-at-risk per quartile
- **CASE + HAVING**: a compound "risk segment" combining contract + tenure + payment
  method, filtered to segments with at least 50 customers
- **RANK() window function**: top customers by value within each contract type
- **Running total window function**: cumulative revenue at risk among churned customers

All results are saved with real output in `sql/results/query_results.md` - for example,
the SQL query for contract-type churn (42.71% / 11.27% / 2.83%) matches the Python EDA
result exactly, which is a useful cross-check that the pipeline is internally consistent.

## 4. Customer Segmentation (`notebooks/04_customer_segmentation.py`)

Simple, explainable rule-based segments (no clustering black box):
- **Tenure stage**: New (≤12 mo) / Growing (13-36 mo) / Loyal (>36 mo)
- **Value tier**: Low / High, split at the dataset's own median `TotalCharges` ($1,394.55)
- Combined into a `SimpleSegment` label. Result: churn drops steadily from
  **New Customer (47%) → Growing (26%) → High-Value Loyal (13%) → Loyal, Low-Value (3%)**,
  confirming tenure and value both matter, but tenure dominates.

## 5. Churn Prediction (`notebooks/05_churn_prediction.py`)

Two models only, as scoped - **Logistic Regression** (interpretable baseline) and
**Random Forest** (captures non-linear interactions):

| Model | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | 0.507 | 0.786 | 0.616 | 0.842 |
| Random Forest | 0.528 | 0.794 | 0.634 | **0.848** |

**Why not accuracy:** churn is imbalanced (~26.5%), so a model that predicts "No Churn"
for everyone would already score ~73% accuracy while catching zero at-risk customers.
Precision/recall/F1/ROC-AUC are used instead, and the model is tuned to prioritize
**recall** (catching real churners) since missing an at-risk customer is more costly to
the business than a wasted retention email.

**Leakage prevention:** `customerID` dropped; train/test split done before fitting the
scaler; only pre-churn, currently-known customer attributes used as features (see the
"Data leakage prevention" note in `notebooks/05_churn_prediction.py` for the full list).

**Top churn drivers (Random Forest):** tenure, two-year contract, Fiber optic internet,
TotalCharges, MonthlyCharges, and electronic check payment - matching the EDA findings
almost exactly, which is a strong signal the model learned the real pattern rather than
noise.

Random Forest's predicted probability (`ChurnProbability`) is carried forward as the
risk score for the retention-priority step, since ranking customers by risk (not just a
binary yes/no) is what the business actually needs.

## 6. Retention Priority (`notebooks/06_retention_priority.py`)

Combines **Churn Probability** (model output) with **Customer Value** (`TotalCharges`,
split into terciles) into 6 priority tiers:

| Priority | Customers | Avg Churn Prob. | Avg Value | Monthly Revenue at Risk | Recommended Action |
|---|---|---|---|---|---|
| **Critical** | 491 | 0.61 | $4,221 | $47,233 | Immediate high-touch outreach + loyalty/upgrade offer |
| **High** | 853 | 0.71 | $1,545 | $72,816 | Proactive email/call campaign with a targeted offer |
| **Low-Cost Retention** | 1,425 | 0.74 | $199 | $86,559 | Automated nudges / self-serve discounts / autopay migration |
| **Maintain** | 1,857 | 0.23 | $5,332 | — | No urgent action; protect the relationship |
| **Monitor** | 1,494 | 0.19 | $1,466 | — | Periodic re-scoring only |
| **No Action Needed** | 923 | 0.24 | $315 | — | Standard service only |

The **Critical** tier - 491 customers worth ~$47K/month - is the clearest ROI case for
a retention team with limited headcount: high value, high probability of leaving, worth
a real phone call rather than an automated email.

## 7. Power BI Dashboard (`powerbi/`)

3 pages as scoped:
1. **Executive Overview** - Total Customers, Churn Rate, High-Risk Customers, Revenue at Risk
2. **Churn Analysis** - churn by contract/tenure/services + a Key Influencers visual
3. **Retention Strategy** - the value-vs-risk scatter, a Critical-priority call list table, and recommendations

See `powerbi/README.md` for the exact DAX measures and layout - it's a copy-paste build
from `powerbi/telco_powerbi_dataset.csv`.

---

## Tech stack

Python (Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn) · MySQL/MariaDB (SQL) · Power BI.
No AI/LLMs, deep learning, Kafka, Docker, APIs, Streamlit, cloud services, or complex
MLOps were used - by design, to keep the project simple, explainable, and fully
reproducible on a laptop.
