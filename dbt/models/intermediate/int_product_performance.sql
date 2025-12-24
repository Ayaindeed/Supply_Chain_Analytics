{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

product_analysis AS (
    SELECT
        product_card_id,
        product_name,
        category_name,
        product_category_id,
        
        -- Agrégations par produit
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(order_item_quantity) AS total_quantity_sold,
        SUM(sales) AS total_sales,
        AVG(sales) AS avg_sales_per_order,
        SUM(order_profit_per_order) AS total_profit,
        AVG(order_profit_per_order) AS avg_profit_per_order,
        
        -- Métriques de performance
        AVG(order_item_profit_ratio) AS avg_profit_ratio,
        AVG(order_item_discount_rate) AS avg_discount_rate,
        
        -- Analyse des retards
        SUM(CASE WHEN late_delivery_risk = 1 THEN 1 ELSE 0 END) AS late_delivery_count,
        CAST(SUM(CASE WHEN late_delivery_risk = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
            NULLIF(COUNT(*), 0) AS late_delivery_rate,
        
        -- Statut du produit
        MAX(product_status) AS product_status,
        AVG(product_price) AS avg_product_price
        
    FROM orders
    GROUP BY 
        product_card_id,
        product_name,
        category_name,
        product_category_id
)

SELECT * FROM product_analysis
