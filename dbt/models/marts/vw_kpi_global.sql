{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH supply_chain AS (
    SELECT * FROM {{ ref('fct_supply_chain') }}
),

kpi_global AS (
    SELECT
        -- Période d'analyse
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_date) AS total_days_active,
        
        -- Métriques de volume
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        
        -- Métriques financières
        SUM(sales) AS total_revenue,
        AVG(sales) AS avg_order_value,
        SUM(order_profit_per_order) AS total_profit,
        AVG(order_profit_per_order) AS avg_profit_per_order,
        SUM(benefit_per_order) AS total_benefit,
        
        -- Métriques de livraison
        AVG(days_for_shipping_real) AS avg_shipping_days,
        AVG(shipping_delay_days) AS avg_delay_days,
        
        -- Taux de performance
        ROUND(
            CAST(CAST(SUM(is_on_time) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 AS NUMERIC), 
            2
        ) AS on_time_delivery_rate,
        
        ROUND(
            CAST(CAST(SUM(CASE WHEN late_delivery_risk = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
            NULLIF(COUNT(*), 0) * 100 AS NUMERIC), 
            2
        ) AS late_delivery_risk_rate,
        
        ROUND(
            CAST(CAST(SUM(is_profitable) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 AS NUMERIC), 
            2
        ) AS profitable_orders_rate,
        
        -- Distribution des performances
        SUM(CASE WHEN performance_score = 'Excellent' THEN 1 ELSE 0 END) AS excellent_orders,
        SUM(CASE WHEN performance_score = 'Good' THEN 1 ELSE 0 END) AS good_orders,
        SUM(CASE WHEN performance_score = 'Average' THEN 1 ELSE 0 END) AS average_orders,
        SUM(CASE WHEN performance_score = 'Poor' THEN 1 ELSE 0 END) AS poor_orders
        
    FROM supply_chain
)

SELECT * FROM kpi_global
