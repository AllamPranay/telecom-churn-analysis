# SQL Analysis Results

Run against telco_churn.customers (7,043 rows) in MySQL/MariaDB.

## Q1: Overall Churn Rate
```
+-----------------+-------------------+----------------+
| total_customers | churned_customers | churn_rate_pct |
+-----------------+-------------------+----------------+
|            7043 |              1869 |          26.54 |
+-----------------+-------------------+----------------+
```

## Q2: Churn Rate by Contract Type
```
+----------------+-----------------+---------+----------------+
| Contract       | total_customers | churned | churn_rate_pct |
+----------------+-----------------+---------+----------------+
| Month-to-month |            3875 |    1655 |          42.71 |
| One year       |            1473 |     166 |          11.27 |
| Two year       |            1695 |      48 |           2.83 |
+----------------+-----------------+---------+----------------+
```

## Q3: Churn Rate by Internet Service
```
+-----------------+-----------------+----------------+--------------------------+-----------------------+
| InternetService | total_customers | churn_rate_pct | pct_with_online_security | pct_with_tech_support |
+-----------------+-----------------+----------------+--------------------------+-----------------------+
| Fiber optic     |            3096 |          41.89 |                    27.10 |                 27.97 |
| DSL             |            2421 |          18.96 |                    48.74 |                 48.66 |
| No              |            1526 |           7.40 |                     0.00 |                  0.00 |
+-----------------+-----------------+----------------+--------------------------+-----------------------+
```

## Q3b: Churn Rate by Payment Method
```
+---------------------------+-----------------+----------------+
| PaymentMethod             | total_customers | churn_rate_pct |
+---------------------------+-----------------+----------------+
| Electronic check          |            2365 |          45.29 |
| Mailed check              |            1612 |          19.11 |
| Bank transfer (automatic) |            1544 |          16.71 |
| Credit card (automatic)   |            1522 |          15.24 |
+---------------------------+-----------------+----------------+
```

## Q4: High-Value Customers by Value Quartile (NTILE window function)
```
+----------------+-----------+-------------------+---------+----------------+-------------------------+
| value_quartile | customers | avg_total_charges | churned | churn_rate_pct | monthly_revenue_at_risk |
+----------------+-----------+-------------------+---------+----------------+-------------------------+
|              1 |      1761 |           5715.99 |     255 |          14.48 |                25338.10 |
|              2 |      1761 |           2393.79 |     405 |          23.00 |                34296.15 |
|              3 |      1761 |            857.20 |     447 |          25.38 |                34088.40 |
|              4 |      1760 |            150.75 |     762 |          43.30 |                45408.20 |
+----------------+-----------+-------------------+---------+----------------+-------------------------+
```
*Quartile 1 = highest-value 25% of customers by lifetime spend.*

## Q5: Compound Risk Segments (CASE + HAVING)
```
+--------------------------------+-----------+---------+----------------+
| risk_segment                   | customers | churned | churn_rate_pct |
+--------------------------------+-----------+---------+----------------+
| New + Flexible Contract        |      1413 |     780 |          55.20 |
| Flexible Contract + Manual Pay |      1170 |     534 |          45.64 |
| Flexible Contract - Other      |      1292 |     341 |          26.39 |
| Locked-in Contract             |      3168 |     214 |           6.76 |
+--------------------------------+-----------+---------+----------------+
```

## Bonus: Top 5 Highest-Value Customers per Contract Type (RANK window function)
```
+------------+----------------+--------------+-------+------------------------+
| customerID | Contract       | TotalCharges | Churn | value_rank_in_contract |
+------------+----------------+--------------+-------+------------------------+
| 9481-IEBZY | Month-to-month |      8061.50 | No    |                      1 |
| 2615-YVMYX | Month-to-month |      7713.55 | No    |                      2 |
| 5804-HYIEZ | Month-to-month |      7554.05 | No    |                      3 |
| 2889-FPWRM | One year       |      8684.80 | Yes   |                      1 |
| 0186-CAERR | One year       |      8309.55 | No    |                      2 |
| 0201-OAMXR | One year       |      8127.60 | Yes   |                      3 |
| 7569-NMZYQ | Two year       |      8672.45 | No    |                      1 |
| 9739-JLPQJ | Two year       |      8670.10 | No    |                      2 |
| 9788-HNGUT | Two year       |      8594.40 | No    |                      3 |
+------------+----------------+--------------+-------+------------------------+
```
