# Churn Prediction - Model Comparison

Trained on 5634 customers, tested on 1409 held-out customers
(stratified 80/20 split, churn rate preserved at ~26.5% in both sets).

## Metrics (on held-out test set)

| Model | Precision | Recall | F1-score | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | 0.507 | 0.786 | 0.616 | 0.842 |
| Random Forest | 0.528 | 0.794 | 0.634 | 0.848 |

## Confusion Matrices (test set, n=1409)

**Logistic Regression**
```
                Predicted No   Predicted Yes
Actual No                749             286
Actual Yes                80             294
```

**Random Forest**
```
                Predicted No   Predicted Yes
Actual No                769             266
Actual Yes                77             297
```

## Business interpretation

- **Why not just accuracy:** the dataset is imbalanced (~26.5% churn), so a model that
  predicts "No Churn" for everyone would already be ~73% accurate while catching zero
  at-risk customers. We optimize for **recall on the churn class** (catching as many
  true churners as possible) balanced against precision (not wasting retention budget
  on customers who were never going to leave), which is why F1-score and ROC-AUC are
  the headline metrics here, not accuracy.
- **Logistic Regression** recalls 78.6% of actual churners on the test
  set, at 50.7% precision. It is fully interpretable - the
  coefficients directly show which factors push risk up or down (see
  `reports/figures/13_feature_importance_lr.png`), which makes it easy to explain to
  non-technical stakeholders and to justify individual retention actions.
- **Random Forest** achieves ROC-AUC of 0.848 vs 0.842 for
  Logistic Regression, meaning it ranks at-risk customers slightly better
  overall. Because ranking customers by risk (not just a yes/no cutoff) is exactly what
  the retention-priority step needs, **Random Forest's predicted probability is used as
  the ChurnProbability score** that feeds the retention priority matrix in the next step.
- **Data leakage prevention:** customerID was dropped, the train/test split happened
  before any scaling was fit, and features were restricted to information a telco would
  actually have about an active customer (no post-churn or future information was used).

## Top churn drivers (Random Forest)

1. tenure: 0.181
2. Contract_Two year: 0.142
3. InternetService_Fiber optic: 0.122
4. TotalCharges: 0.114
5. MonthlyCharges: 0.090
6. PaymentMethod_Electronic check: 0.074
7. InternetService_No: 0.064
8. Contract_One year: 0.054

These line up with the EDA findings: contract type, tenure, and monthly charges are the
dominant drivers of churn risk - which is reassuring, since it means the model isn't
picking up on some spurious or leaky pattern, it's confirming the same story the business
already sees in the raw numbers.
