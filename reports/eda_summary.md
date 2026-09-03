# EDA Summary - Customer Churn & Retention Intelligence

Dataset: 7043 customers, overall churn rate 26.5%

1. **Overall churn rate: 26.5%** (1869 of 7043 customers). Roughly 1 in 4 customers is leaving - retention needs to be an active, budgeted program, not an afterthought.

2. **Contract type is the single strongest churn signal.** Month-to-month customers churn at 42.7%, versus 11.3% for one-year and 2.8% for two-year contracts. Converting month-to-month customers onto annual contracts (with a modest incentive) is likely the highest-leverage retention lever available.

3. **Churn is heavily front-loaded.** Customers in their first 6 months churn at 52.9%, compared to only 9.5% for customers with 49-72 months of tenure. The first 6 months is the critical window for onboarding and early-life retention efforts.

4. **Higher-paying customers churn more, not less.** The top monthly-charges quartile churns at 32.9% vs 11.2% in the lowest quartile. These customers are usually on Fiber optic internet with several premium add-ons - they are paying the most and are also the most price-sensitive/at-risk group, making them a priority for proactive retention rather than up-sell.

5. **Fiber optic customers churn far more than DSL or no-internet customers**: 41.9% vs 19.0% (DSL) and 7.4% (no internet). This likely reflects both higher fiber pricing and possibly service/reliability complaints - worth a service-quality review alongside the pricing story.

6. **Electronic check payers churn the most** at 45.3%, roughly double the rate of customers on automatic bank transfer or credit card payments (16.7% / 15.2%). Migrating electronic-check customers onto autopay is a low-cost, high-impact retention action.

7. **Customers without security/support add-ons churn substantially more.** For example, customers without Online Security churn at 31.3% vs 14.6% for those who have it, and customers without Tech Support churn at 31.2% vs 15.2% with it. Bundling security/support into onboarding (or offering a free trial) could reduce churn.

8. **Tenure is negatively correlated with churn (r = -0.35)** and MonthlyCharges is positively correlated with churn (r = 0.19). Together these confirm the core churn story: new, high-paying customers on flexible contracts are the highest-risk segment.

