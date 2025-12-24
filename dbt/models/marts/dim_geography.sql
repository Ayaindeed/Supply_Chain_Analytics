/*
    Dimension Geography - Hiérarchie géographique
    City -> State -> Country -> Region -> Market
*/

{{ config(
    materialized='table',
    schema='marts'
) }}

WITH geography_hierarchy AS (
    SELECT DISTINCT
        order_city,
        order_state,
        order_country,
        order_region,
        market,
        latitude_dest,
        longitude_dest
    FROM {{ source('raw_data', 'supply_chain_raw') }}
    WHERE order_country IS NOT NULL
),

geography_metrics AS (
    SELECT
        g.order_city,
        g.order_state,
        g.order_country,
        g.order_region,
        g.market,
        g.latitude_dest,
        g.longitude_dest,
        
        -- Métriques par géographie
        COUNT(DISTINCT s.customer_id) as total_customers,
        COUNT(DISTINCT s.order_id) as total_orders,
        SUM(s.sales) as total_sales,
        AVG(s.sales) as avg_sales,
        AVG(CASE WHEN s.late_delivery_risk = 1 THEN 1.0 ELSE 0.0 END) as late_delivery_rate,
        AVG(s.shipping_delay_days) as avg_shipping_delay
        
    FROM geography_hierarchy g
    LEFT JOIN {{ ref('int_delivery_performance') }} s
        ON g.order_city = s.order_city
        AND g.order_state = s.order_state
        AND g.order_country = s.order_country
    GROUP BY 1, 2, 3, 4, 5, 6, 7
)

SELECT
    ROW_NUMBER() OVER (ORDER BY total_sales DESC) as geography_id,
    
    -- Hiérarchie géographique
    order_city as city,
    order_state as state,
    order_country as country,
    order_region as region,
    market,
    
    -- Coordonnées
    latitude_dest as latitude,
    longitude_dest as longitude,
    
    -- Métriques
    total_customers,
    total_orders,
    ROUND(CAST(total_sales AS NUMERIC), 2) as total_sales,
    ROUND(CAST(avg_sales AS NUMERIC), 2) as avg_order_value,
    ROUND(CAST(late_delivery_rate * 100 AS NUMERIC), 2) as late_delivery_rate_pct,
    ROUND(CAST(avg_shipping_delay AS NUMERIC), 2) as avg_shipping_delay_days
    
FROM geography_metrics
ORDER BY total_sales DESC
