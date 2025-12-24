{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

delivery_metrics AS (
    SELECT
        order_id,
        order_item_id,
        order_date,
        customer_id,
        product_card_id,
        
        -- Métriques de délai
        days_for_shipping_real,
        days_for_shipment_scheduled,
        days_for_shipping_real - days_for_shipment_scheduled AS shipping_delay_days,
        
        -- Classification des retards
        CASE 
            WHEN days_for_shipping_real - days_for_shipment_scheduled <= 0 THEN 'On Time'
            WHEN days_for_shipping_real - days_for_shipment_scheduled BETWEEN 1 AND 3 THEN 'Slightly Late'
            WHEN days_for_shipping_real - days_for_shipment_scheduled BETWEEN 4 AND 7 THEN 'Late'
            ELSE 'Very Late'
        END AS delay_category,
        
        -- Indicateurs de performance
        late_delivery_risk,
        delivery_status,
        shipping_mode,
        
        -- Informations géographiques
        order_region,
        order_country,
        order_city,
        order_state,
        market,
        
        -- Métriques financières
        sales,
        order_profit_per_order,
        benefit_per_order
        
    FROM orders
)

SELECT * FROM delivery_metrics
