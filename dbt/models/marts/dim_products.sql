{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH product_perf AS (
    SELECT * FROM {{ ref('int_product_performance') }}
),

final AS (
    SELECT
        product_card_id,
        product_name,
        category_name,
        product_category_id,
        
        -- Métriques de vente
        total_orders,
        total_quantity_sold,
        total_sales,
        avg_sales_per_order,
        total_profit,
        avg_profit_per_order,
        
        -- Métriques de performance
        avg_profit_ratio,
        avg_discount_rate,
        
        -- Analyse des retards
        late_delivery_count,
        ROUND(CAST(late_delivery_rate * 100 AS NUMERIC), 2) AS late_delivery_rate_pct,
        
        -- Statut et prix
        product_status,
        avg_product_price,
        
        -- Classification ABC
        CASE
            WHEN total_sales >= (SELECT PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY total_sales) FROM product_perf) THEN 'A'
            WHEN total_sales >= (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_sales) FROM product_perf) THEN 'B'
            ELSE 'C'
        END AS abc_classification,
        
        -- Niveau de risque
        CASE
            WHEN late_delivery_rate > 0.3 THEN 'High Risk'
            WHEN late_delivery_rate > 0.15 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS delivery_risk_level
        
    FROM product_perf
)

SELECT * FROM final
