-- =====================================================================
-- 01_schema.sql
-- Customer Churn & Retention Intelligence
-- Creates the database and the customers table that holds the cleaned
-- Telco Customer Churn dataset (loaded via 02_load_data.py).
-- =====================================================================

CREATE DATABASE IF NOT EXISTS telco_churn;
USE telco_churn;

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customerID          VARCHAR(20)   PRIMARY KEY,
    gender               VARCHAR(10),
    SeniorCitizen        VARCHAR(5),
    Partner              VARCHAR(5),
    Dependents           VARCHAR(5),
    tenure               INT,
    PhoneService         VARCHAR(5),
    MultipleLines        VARCHAR(5),
    InternetService      VARCHAR(20),
    OnlineSecurity       VARCHAR(5),
    OnlineBackup         VARCHAR(5),
    DeviceProtection     VARCHAR(5),
    TechSupport          VARCHAR(5),
    StreamingTV          VARCHAR(5),
    StreamingMovies      VARCHAR(5),
    Contract             VARCHAR(20),
    PaperlessBilling     VARCHAR(5),
    PaymentMethod        VARCHAR(30),
    MonthlyCharges       DECIMAL(8,2),
    TotalCharges         DECIMAL(10,2),
    Churn                VARCHAR(5),
    ChurnFlag            TINYINT
);

-- Helpful indexes for the analytical queries below
CREATE INDEX idx_contract ON customers (Contract);
CREATE INDEX idx_internet ON customers (InternetService);
CREATE INDEX idx_payment  ON customers (PaymentMethod);
CREATE INDEX idx_churn    ON customers (Churn);
