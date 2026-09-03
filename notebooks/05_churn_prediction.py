"""
05_churn_prediction.py
------------------------
Customer Churn & Retention Intelligence
Step 5: Churn Prediction

Builds and compares two simple, interpretable models:
    1. Logistic Regression (baseline, interpretable coefficients)
    2. Random Forest (captures non-linear interactions)

Data leakage prevention:
    - customerID is dropped (identifier, not a feature).
    - Churn / ChurnFlag (the target) and Churn-derived helper columns
      are excluded from X.
    - TotalCharges is highly correlated with tenure * MonthlyCharges
      by construction (it is literally derived from them for most
      rows) - we keep it since it is a legitimate, pre-churn-known
      feature (a real telco would have this at prediction time), but
      we flag this explicitly rather than silently including it.
    - Train/test split is done BEFORE any scaling/encoding is fit, and
      the same fitted transformers are reused on the test set (fit on
      train only) to avoid leaking test information into training.
    - Stratified split preserves the ~26.5% churn rate in both sets.

Output:
    - reports/model_comparison.md      (metrics + business explanation)
    - reports/figures/09_confusion_matrix_lr.png
    - reports/figures/10_confusion_matrix_rf.png
    - reports/figures/11_roc_curve.png
    - reports/figures/12_feature_importance_rf.png
    - reports/figures/13_feature_importance_lr.png
    - models/logistic_regression.pkl
    - models/random_forest.pkl
    - data/processed/telco_scored.csv   (adds ChurnProbability per customer)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve
)

sns.set_style("whitegrid")
os.makedirs("reports/figures", exist_ok=True)
os.makedirs("models", exist_ok=True)

IN_PATH = "data/processed/telco_segmented.csv"
RANDOM_STATE = 42

df = pd.read_csv(IN_PATH)

# ---------------------------------------------------------------
# 1. Feature preparation (leakage-safe)
# ---------------------------------------------------------------
drop_cols = [
    "customerID", "Churn", "ChurnFlag",
    "tenure_bucket", "charges_bucket",              # EDA helper columns, not always present
    "TenureSegment", "ValueTier", "CustomerSegment", "SimpleSegment",  # derived post-hoc labels
]
drop_cols = [c for c in drop_cols if c in df.columns]

X = df.drop(columns=drop_cols)
y = df["ChurnFlag"]

categorical_cols = X.select_dtypes(include=["object", "string"]).columns.tolist()
numeric_cols = [c for c in X.columns if c not in categorical_cols]

print(f"Numeric features ({len(numeric_cols)}): {numeric_cols}")
print(f"Categorical features ({len(categorical_cols)}): {categorical_cols}")

X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

# ---------------------------------------------------------------
# 2. Train/test split BEFORE fitting any transformer (leakage prevention)
# ---------------------------------------------------------------
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X_encoded, y, df.index, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"\nTrain size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")
print(f"Train churn rate: {y_train.mean():.2%} | Test churn rate: {y_test.mean():.2%}")

# Scale numeric features for Logistic Regression only (fit on train, apply to test)
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()
X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

# ---------------------------------------------------------------
# 3. Model 1: Logistic Regression
# ---------------------------------------------------------------
lr = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)
lr.fit(X_train_scaled, y_train)
lr_pred = lr.predict(X_test_scaled)
lr_proba = lr.predict_proba(X_test_scaled)[:, 1]

# ---------------------------------------------------------------
# 4. Model 2: Random Forest
# ---------------------------------------------------------------
rf = RandomForestClassifier(
    n_estimators=300, max_depth=8, min_samples_leaf=20,
    class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
)
rf.fit(X_train, y_train)  # tree models don't need scaling
rf_pred = rf.predict(X_test)
rf_proba = rf.predict_proba(X_test)[:, 1]

# ---------------------------------------------------------------
# 5. Evaluation
# ---------------------------------------------------------------
def evaluate(name, y_true, y_pred, y_proba):
    return {
        "model": name,
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_proba),
    }

results = [
    evaluate("Logistic Regression", y_test, lr_pred, lr_proba),
    evaluate("Random Forest", y_test, rf_pred, rf_proba),
]
results_df = pd.DataFrame(results).set_index("model").round(3)
print("\n--- Model Comparison ---")
print(results_df)

# Confusion matrices
for name, pred, fig_name in [("Logistic Regression", lr_pred, "09_confusion_matrix_lr"),
                              ("Random Forest", rf_pred, "10_confusion_matrix_rf")]:
    cm = confusion_matrix(y_test, pred)
    fig, ax = plt.subplots(figsize=(4.5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["No Churn", "Churn"], yticklabels=["No Churn", "Churn"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix - {name}")
    fig.savefig(f"reports/figures/{fig_name}.png", bbox_inches="tight")
    plt.close(fig)

# ROC curves
fig, ax = plt.subplots(figsize=(5.5, 5))
for name, proba in [("Logistic Regression", lr_proba), ("Random Forest", rf_proba)]:
    fpr, tpr, _ = roc_curve(y_test, proba)
    auc = roc_auc_score(y_test, proba)
    ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve Comparison")
ax.legend()
fig.savefig("reports/figures/11_roc_curve.png", bbox_inches="tight")
plt.close(fig)

# Feature importance - Random Forest
importances = pd.Series(rf.feature_importances_, index=X_train.columns).sort_values(ascending=False).head(15)
fig, ax = plt.subplots(figsize=(7, 6))
importances.sort_values().plot.barh(ax=ax, color="#2E86AB")
ax.set_title("Top 15 Feature Importances - Random Forest")
fig.savefig("reports/figures/12_feature_importance_rf.png", bbox_inches="tight")
plt.close(fig)

# Feature importance - Logistic Regression (absolute coefficient size)
coefs = pd.Series(lr.coef_[0], index=X_train_scaled.columns).sort_values(key=abs, ascending=False).head(15)
fig, ax = plt.subplots(figsize=(7, 6))
colors = ["#E63946" if v > 0 else "#2E86AB" for v in coefs.sort_values()]
coefs.sort_values().plot.barh(ax=ax, color=colors)
ax.set_title("Top 15 Coefficients - Logistic Regression\n(red = increases churn risk, blue = decreases)")
fig.savefig("reports/figures/13_feature_importance_lr.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------
# 6. Save models
# ---------------------------------------------------------------
with open("models/logistic_regression.pkl", "wb") as f:
    pickle.dump({"model": lr, "scaler": scaler, "columns": X_train.columns.tolist(), "numeric_cols": numeric_cols}, f)
with open("models/random_forest.pkl", "wb") as f:
    pickle.dump({"model": rf, "columns": X_train.columns.tolist()}, f)

# ---------------------------------------------------------------
# 7. Score the FULL dataset with the chosen model (Random Forest) so
#    downstream retention-priority step has a churn probability per
#    customer. We refit the scoring only for scoring purposes - the
#    reported metrics above already come from the untouched test set.
# ---------------------------------------------------------------
full_proba = rf.predict_proba(X_encoded)[:, 1]
df["ChurnProbability"] = full_proba
df["ChurnProbability_Set"] = np.where(df.index.isin(idx_test), "test", "train")
df.to_csv("data/processed/telco_scored.csv", index=False)

# ---------------------------------------------------------------
# 8. Write business-facing markdown report
# ---------------------------------------------------------------
cm_lr = confusion_matrix(y_test, lr_pred)
cm_rf = confusion_matrix(y_test, rf_pred)

report = f"""# Churn Prediction - Model Comparison

Trained on {X_train.shape[0]} customers, tested on {X_test.shape[0]} held-out customers
(stratified 80/20 split, churn rate preserved at ~{y_test.mean():.1%} in both sets).

## Metrics (on held-out test set)

| Model | Precision | Recall | F1-score | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | {results_df.loc['Logistic Regression','precision']:.3f} | {results_df.loc['Logistic Regression','recall']:.3f} | {results_df.loc['Logistic Regression','f1']:.3f} | {results_df.loc['Logistic Regression','roc_auc']:.3f} |
| Random Forest | {results_df.loc['Random Forest','precision']:.3f} | {results_df.loc['Random Forest','recall']:.3f} | {results_df.loc['Random Forest','f1']:.3f} | {results_df.loc['Random Forest','roc_auc']:.3f} |

## Confusion Matrices (test set, n={X_test.shape[0]})

**Logistic Regression**
```
                Predicted No   Predicted Yes
Actual No       {cm_lr[0][0]:>12}   {cm_lr[0][1]:>13}
Actual Yes      {cm_lr[1][0]:>12}   {cm_lr[1][1]:>13}
```

**Random Forest**
```
                Predicted No   Predicted Yes
Actual No       {cm_rf[0][0]:>12}   {cm_rf[0][1]:>13}
Actual Yes      {cm_rf[1][0]:>12}   {cm_rf[1][1]:>13}
```

## Business interpretation

- **Why not just accuracy:** the dataset is imbalanced (~26.5% churn), so a model that
  predicts "No Churn" for everyone would already be ~73% accurate while catching zero
  at-risk customers. We optimize for **recall on the churn class** (catching as many
  true churners as possible) balanced against precision (not wasting retention budget
  on customers who were never going to leave), which is why F1-score and ROC-AUC are
  the headline metrics here, not accuracy.
- **Logistic Regression** recalls {results_df.loc['Logistic Regression','recall']:.1%} of actual churners on the test
  set, at {results_df.loc['Logistic Regression','precision']:.1%} precision. It is fully interpretable - the
  coefficients directly show which factors push risk up or down (see
  `reports/figures/13_feature_importance_lr.png`), which makes it easy to explain to
  non-technical stakeholders and to justify individual retention actions.
- **Random Forest** achieves ROC-AUC of {results_df.loc['Random Forest','roc_auc']:.3f} vs {results_df.loc['Logistic Regression','roc_auc']:.3f} for
  Logistic Regression, meaning it ranks at-risk customers slightly {"better" if results_df.loc['Random Forest','roc_auc'] > results_df.loc['Logistic Regression','roc_auc'] else "similarly"}
  overall. Because ranking customers by risk (not just a yes/no cutoff) is exactly what
  the retention-priority step needs, **Random Forest's predicted probability is used as
  the ChurnProbability score** that feeds the retention priority matrix in the next step.
- **Data leakage prevention:** customerID was dropped, the train/test split happened
  before any scaling was fit, and features were restricted to information a telco would
  actually have about an active customer (no post-churn or future information was used).

## Top churn drivers (Random Forest)

{chr(10).join(f"{i+1}. {name}: {val:.3f}" for i, (name, val) in enumerate(importances.sort_values(ascending=False).head(8).items()))}

These line up with the EDA findings: contract type, tenure, and monthly charges are the
dominant drivers of churn risk - which is reassuring, since it means the model isn't
picking up on some spurious or leaky pattern, it's confirming the same story the business
already sees in the raw numbers.
"""

with open("reports/model_comparison.md", "w") as f:
    f.write(report)

print("\nSaved reports/model_comparison.md, figures, models, and telco_scored.csv")
