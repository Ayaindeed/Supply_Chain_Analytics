/*
    Dimension Customers - Profil client avec métriques agrégées
*/

{{ config(
    materialized='table',
    schema='marts'
) }}

WITH customer_orders AS (
    SELECT
        customer_id,
        customer_fname,
        customer_lname,
        customer_segment,
        customer_city,
        customer_state,
        customer_country,
        customer_zipcode,
        
        -- Agrégations
        COUNT(DISTINCT order_id) as total_orders,
        SUM(sales) as total_sales,
        AVG(sales) as avg_order_value,
        SUM(order_profit_per_order) as total_profit,
        
        -- Comportement
        AVG(CASE WHEN late_delivery_risk = 1 THEN 1.0 ELSE 0.0 END) as late_delivery_rate,
        AVG(CASE WHEN delivery_status = 'Shipping canceled' THEN 1.0 ELSE 0.0 END) as cancellation_rate,
        
        -- Temporalité
        MIN(order_date_dateorders::date) as first_order_date,
        MAX(order_date_dateorders::date) as last_order_date,
        
        -- Produits
        COUNT(DISTINCT product_card_id) as unique_products_purchased,
        COUNT(DISTINCT category_name) as unique_categories_purchased
        
    FROM {{ source('raw_data', 'supply_chain_raw') }}
    WHERE customer_id IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
),

customer_segmentation AS (
    SELECT
        *,
        
        -- Segmentation RFM simplifiée
        CASE
            WHEN total_orders >= 10 AND avg_order_value > 500 THEN 'VIP'
            WHEN total_orders >= 5 AND avg_order_value > 300 THEN 'High Value'
            WHEN total_orders >= 3 THEN 'Regular'
            WHEN total_orders >= 2 THEN 'Occasional'
            ELSE 'New'
        END as customer_tier,
        
        -- Lifetime value
        ROUND(CAST(total_sales AS NUMERIC), 2) as customer_lifetime_value,
        
        -- Jours depuis dernière commande
        CURRENT_DATE - last_order_date as days_since_last_order,
        
        -- Statut activité
        CASE
            WHEN CURRENT_DATE - last_order_date <= 90 THEN 'Active'
            WHEN CURRENT_DATE - last_order_date <= 180 THEN 'At Risk'
            ELSE 'Inactive'
        END as customer_status
        
    FROM customer_orders
)

SELECT
    customer_id,
    customer_fname || ' ' || customer_lname as customer_full_name,
    customer_segment,
    customer_city,
    customer_state,
    customer_country,
    customer_zipcode,
    
    total_orders,
    total_sales,
    avg_order_value,
    total_profit,
    
    late_delivery_rate,
    cancellation_rate,
    
    first_order_date,
    last_order_date,
    days_since_last_order,
    
    unique_products_purchased,
    unique_categories_purchased,
    
    customer_tier,
    customer_lifetime_value,
    customer_status
    
FROM customer_segmentation
ORDER BY total_sales DESC
