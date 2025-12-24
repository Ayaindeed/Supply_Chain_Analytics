{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH delivery_perf AS (
    SELECT * FROM {{ ref('int_delivery_performance') }}
),

final AS (
    SELECT
        order_id,
        order_item_id,
        order_date,
        customer_id,
        
        -- Dimensions temporelles
        EXTRACT(YEAR FROM order_date) AS order_year,
        EXTRACT(MONTH FROM order_date) AS order_month,
        EXTRACT(QUARTER FROM order_date) AS order_quarter,
        EXTRACT(DAY FROM order_date) AS order_day,
        TO_CHAR(order_date, 'Day') AS order_day_name,
        
        -- Métriques de livraison
        days_for_shipping_real,
        days_for_shipment_scheduled,
        shipping_delay_days,
        delay_category,
        late_delivery_risk,
        delivery_status,
        
        -- Dimensions géographiques
        order_region,
        order_country,
        order_city,
        market,
        
        -- Métriques financières
        sales,
        order_profit_per_order,
        benefit_per_order,
        
        -- KPIs calculés
        CASE 
            WHEN shipping_delay_days <= 0 THEN 1 
            ELSE 0 
        END AS is_on_time,
        
        CASE 
            WHEN order_profit_per_order > 0 THEN 1 
            ELSE 0 
        END AS is_profitable,
        
        -- Scoring de performance
        CASE
            WHEN shipping_delay_days <= 0 AND order_profit_per_order > 0 THEN 'Excellent'
            WHEN shipping_delay_days <= 3 AND order_profit_per_order > 0 THEN 'Good'
            WHEN shipping_delay_days <= 7 OR order_profit_per_order > 0 THEN 'Average'
            ELSE 'Poor'
        END AS performance_score
        
    FROM delivery_perf
)

SELECT * FROM final
