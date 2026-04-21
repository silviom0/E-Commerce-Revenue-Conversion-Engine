-- =============================================================
-- ecommerce_queries.sql
-- Schema + analytical queries for the e-commerce dataset
-- Compatible with PostgreSQL
-- =============================================================

-- ─── CREATE TABLE ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ecommerce_interactions (
    Customer_ID           VARCHAR(12)   PRIMARY KEY,
    Acquisition_Channel   VARCHAR(20)   NOT NULL,
    Ad_Spend              NUMERIC(8,2),
    Cart_Value            NUMERIC(8,2),
    Checkout_Completed    BOOLEAN       NOT NULL,
    Days_As_Customer      INT           NOT NULL
);

-- ─── LOAD DATA ───────────────────────────────────────────────
-- COPY ecommerce_interactions
-- FROM '/path/to/ecommerce_interactions_clean.csv'
-- DELIMITER ',' CSV HEADER;


-- ─── QUERY 1: CAC & AOV by Acquisition Channel ───────────────
-- CAC = total ad spend / number of conversions
-- AOV = total converted revenue / number of conversions
SELECT
    Acquisition_Channel,
    COUNT(*)                                            AS Total_Visitors,
    SUM(CASE WHEN Checkout_Completed THEN 1 ELSE 0 END) AS Conversions,
    ROUND(
        100.0 * SUM(CASE WHEN Checkout_Completed THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                   AS Conversion_Rate_Pct,
    ROUND(
        SUM(Ad_Spend)
        / NULLIF(SUM(CASE WHEN Checkout_Completed THEN 1 ELSE 0 END), 0),
        2
    )                                                   AS CAC,
    ROUND(
        SUM(CASE WHEN Checkout_Completed THEN Cart_Value ELSE 0 END)
        / NULLIF(SUM(CASE WHEN Checkout_Completed THEN 1 ELSE 0 END), 0),
        2
    )                                                   AS AOV,
    ROUND(
        SUM(CASE WHEN Checkout_Completed THEN Cart_Value ELSE 0 END)
        / NULLIF(SUM(Ad_Spend), 0),
        2
    )                                                   AS ROAS
FROM ecommerce_interactions
GROUP BY Acquisition_Channel
ORDER BY ROAS DESC;


-- ─── QUERY 2: Checkout Drop-off Analysis ─────────────────────
SELECT
    Acquisition_Channel,
    COUNT(*)                                              AS Total_Carts,
    SUM(CASE WHEN NOT Checkout_Completed THEN 1 ELSE 0 END) AS Abandoned,
    ROUND(
        100.0 * SUM(CASE WHEN NOT Checkout_Completed THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                     AS Abandonment_Rate_Pct,
    ROUND(
        SUM(CASE WHEN NOT Checkout_Completed THEN Cart_Value ELSE 0 END),
        2
    )                                                     AS Abandoned_Revenue
FROM ecommerce_interactions
GROUP BY Acquisition_Channel
ORDER BY Abandonment_Rate_Pct DESC;


-- ─── QUERY 3: High-Value Churned Customers (recovery targets) ─
-- Customers who never converted but have high cart values
SELECT
    Customer_ID,
    Acquisition_Channel,
    Cart_Value,
    Ad_Spend,
    Days_As_Customer
FROM ecommerce_interactions
WHERE Checkout_Completed = FALSE
  AND Cart_Value > 100
ORDER BY Cart_Value DESC
LIMIT 25;


-- ─── QUERY 4: LTV Proxy by Channel ───────────────────────────
SELECT
    Acquisition_Channel,
    ROUND(AVG(
        CASE WHEN Checkout_Completed
             THEN Cart_Value * (1 + Days_As_Customer / 180.0)
             ELSE 0 END
    ), 2)                                AS Avg_LTV_Estimate,
    ROUND(AVG(Days_As_Customer), 1)      AS Avg_Days_As_Customer,
    ROUND(AVG(Cart_Value), 2)            AS Avg_Cart_Value
FROM ecommerce_interactions
GROUP BY Acquisition_Channel
ORDER BY Avg_LTV_Estimate DESC;


-- ─── QUERY 5: Cohort — Early vs Late Converters ──────────────
SELECT
    CASE
        WHEN Days_As_Customer < 30  THEN '0–30 days'
        WHEN Days_As_Customer < 90  THEN '31–90 days'
        WHEN Days_As_Customer < 180 THEN '91–180 days'
        ELSE '180+ days'
    END                                                    AS Cohort,
    COUNT(*)                                               AS Customers,
    ROUND(
        100.0 * SUM(CASE WHEN Checkout_Completed THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                      AS Conversion_Rate_Pct,
    ROUND(AVG(Cart_Value), 2)                              AS Avg_Cart_Value
FROM ecommerce_interactions
GROUP BY 1
ORDER BY MIN(Days_As_Customer);
