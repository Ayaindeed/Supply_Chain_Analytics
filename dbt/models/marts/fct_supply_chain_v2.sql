{{
    config(
        materialized='table',
        schema='marts'
    )
}}

/*
    Table de faits centrale - Supply Chain
    Connectée à 5 dimensions : Date, Customers, Products, Geography, Shipping
*/

WITH delivery_perf AS (
    SELECT * FROM {{ ref('int_delivery_performance') }}
),

-- Jointure avec dim_date pour récupérer date_id
dates AS (
    SELECT 
        date_id,
        date_value
    FROM {{ ref('dim_date') }}
),

-- Jointure avec dim_geography pour récupérer geography_id
geography AS (
    SELECT
        geography_id,
        city,
        state,
        country,
        region,
        market
    FROM {{ ref('dim_geography') }}
),

-- Jointure avec dim_shipping pour récupérer shipping_id  
shipping AS (
    SELECT
        shipping_id,
        shipping_mode,
        delivery_status
    FROM {{ ref('dim_shipping') }}
),

final AS (
    SELECT
        -- Clés primaires
        dp.order_id,
        dp.order_item_id,
        
        -- Foreign Keys vers dimensions
        d.date_id,
        dp.customer_id,  -- FK vers dim_customers
        dp.product_card_id,   -- FK vers dim_products
        g.geography_id,  -- FK vers dim_geography
        s.shipping_id,   -- FK vers dim_shipping
        
        -- Dimensions dégénérées (garder pour compatibilité et filtrage rapide)
        dp.order_date,
        EXTRACT(YEAR FROM dp.order_date) AS order_year,
        EXTRACT(MONTH FROM dp.order_date) AS order_month,
        EXTRACT(QUARTER FROM dp.order_date) AS order_quarter,
        EXTRACT(DAY FROM dp.order_date) AS order_day,
        
        -- Métriques de livraison
        dp.days_for_shipping_real,
        dp.days_for_shipment_scheduled,
        dp.shipping_delay_days,
        dp.delay_category,
        dp.late_delivery_risk,
        dp.delivery_status,
        
        -- Métriques financières
        dp.sales,
        dp.order_profit_per_order,
        dp.benefit_per_order,
        
        -- KPIs calculés
        CASE 
            WHEN dp.shipping_delay_days <= 0 THEN 1 
            ELSE 0 
        END AS is_on_time,
        
        CASE 
            WHEN dp.order_profit_per_order > 0 THEN 1 
            ELSE 0 
        END AS is_profitable,
        
        -- Score de performance
        CASE
            WHEN dp.shipping_delay_days <= -2 THEN 'Excellent'
            WHEN dp.shipping_delay_days <= 0 THEN 'Good'
            WHEN dp.shipping_delay_days <= 3 THEN 'Average'
            WHEN dp.shipping_delay_days <= 7 THEN 'Poor'
            ELSE 'Critical'
        END AS performance_score
        
    FROM delivery_perf dp
    
    -- Jointures avec dimensions
    LEFT JOIN dates d 
        ON dp.order_date::date = d.date_value
    
    LEFT JOIN geography g
        ON dp.order_city = g.city
        AND dp.order_country = g.country
        AND dp.order_region = g.region
    
    LEFT JOIN shipping s
        ON dp.shipping_mode = s.shipping_mode
        AND dp.delivery_status = s.delivery_status
)

SELECT * FROM final
