-- =====================================================================
-- 02_analysis_queries.sql
-- Customer Churn & Retention Intelligence - SQL Analysis
-- Run against: telco_churn.customers (7,043 rows)
-- =====================================================================
USE telco_churn;

-- ---------------------------------------------------------------------
-- Q1. Overall churn rate
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                             AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)        AS churned_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers;


-- ---------------------------------------------------------------------
-- Q2. Churn rate by contract type
-- ---------------------------------------------------------------------
SELECT
    Contract,
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)         AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;


-- ---------------------------------------------------------------------
-- Q3. Churn rate by service (Internet Service + key add-ons)
-- ---------------------------------------------------------------------
SELECT
    InternetService,
    COUNT(*)                                              AS total_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_with_online_security,
    ROUND(100.0 * SUM(CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)    AS pct_with_tech_support
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- Churn by payment method (another key "service experience" cut)
SELECT
    PaymentMethod,
    COUNT(*)                                              AS total_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;


-- ---------------------------------------------------------------------
-- Q4. High-value customers (top spenders) and their churn exposure
--     "High value" = top 25% by TotalCharges (a CTE computes the cutoff)
-- ---------------------------------------------------------------------
WITH ranked AS (
    SELECT
        customerID,
        TotalCharges,
        MonthlyCharges,
        tenure,
        Churn,
        NTILE(4) OVER (ORDER BY TotalCharges DESC) AS value_quartile
    FROM customers
)
SELECT
    value_quartile,
    COUNT(*)                                              AS customers,
    ROUND(AVG(TotalCharges), 2)                           AS avg_total_charges,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)         AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_at_risk
FROM ranked
GROUP BY value_quartile
ORDER BY value_quartile;

-- Top 20 highest-value customers who are still active but flagged
-- as high-risk (Month-to-month contract = highest risk contract type)
SELECT
    customerID, tenure, MonthlyCharges, TotalCharges, Contract, PaymentMethod
FROM customers
WHERE Churn = 'No'
  AND Contract = 'Month-to-month'
ORDER BY TotalCharges DESC
LIMIT 20;


-- ---------------------------------------------------------------------
-- Q5. Customer groups with high churn (compound segment using CASE)
--     Combines contract + tenure + payment method into a risk label
-- ---------------------------------------------------------------------
WITH segmented AS (
    SELECT
        customerID,
        Churn,
        MonthlyCharges,
        CASE
            WHEN Contract = 'Month-to-month' AND tenure <= 6 THEN 'New + Flexible Contract'
            WHEN Contract = 'Month-to-month' AND PaymentMethod = 'Electronic check' THEN 'Flexible Contract + Manual Pay'
            WHEN Contract = 'Month-to-month' THEN 'Flexible Contract - Other'
            WHEN Contract IN ('One year', 'Two year') THEN 'Locked-in Contract'
            ELSE 'Other'
        END AS risk_segment
    FROM customers
)
SELECT
    risk_segment,
    COUNT(*)                                              AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)         AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM segmented
GROUP BY risk_segment
HAVING COUNT(*) >= 50          -- ignore tiny/noisy segments
ORDER BY churn_rate_pct DESC;


-- ---------------------------------------------------------------------
-- Bonus: Window function - rank customers by TotalCharges within each
-- contract type, useful for "who are our highest value customers per
-- contract segment" style questions from stakeholders.
-- ---------------------------------------------------------------------
SELECT *
FROM (
    SELECT
        customerID,
        Contract,
        TotalCharges,
        Churn,
        RANK() OVER (PARTITION BY Contract ORDER BY TotalCharges DESC) AS value_rank_in_contract
    FROM customers
) ranked
WHERE value_rank_in_contract <= 5
ORDER BY Contract, value_rank_in_contract;


-- ---------------------------------------------------------------------
-- Bonus: Running/cumulative revenue at risk from churned customers,
-- ordered by MonthlyCharges descending (illustrates a window function
-- running total - useful for a "how many top-risk customers do we need
-- to save to recover $X of at-risk revenue" style analysis)
-- ---------------------------------------------------------------------
SELECT
    customerID,
    MonthlyCharges,
    SUM(MonthlyCharges) OVER (ORDER BY MonthlyCharges DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_monthly_revenue_at_risk
FROM customers
WHERE Churn = 'Yes'
ORDER BY MonthlyCharges DESC
LIMIT 20;
