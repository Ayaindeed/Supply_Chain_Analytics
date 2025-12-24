/*
    Dimension Shipping - Modes de livraison et statuts
*/

{{ config(
    materialized='table',
    schema='marts'
) }}

WITH shipping_combinations AS (
    SELECT DISTINCT
        shipping_mode,
        delivery_status,
        
        -- Agrégation pour avoir des stats par combinaison
        COUNT(*) OVER (PARTITION BY shipping_mode, delivery_status) as occurrences,
        AVG(days_for_shipping_real) OVER (PARTITION BY shipping_mode, delivery_status) as avg_actual_days,
        AVG(days_for_shipment_scheduled) OVER (PARTITION BY shipping_mode, delivery_status) as avg_scheduled_days,
        AVG(shipping_delay_days) OVER (PARTITION BY shipping_mode, delivery_status) as avg_delay_days,
        SUM(CASE WHEN late_delivery_risk = 1 THEN 1 ELSE 0 END) OVER (PARTITION BY shipping_mode, delivery_status)::float / 
            COUNT(*) OVER (PARTITION BY shipping_mode, delivery_status) as late_risk_rate
        
    FROM {{ ref('int_delivery_performance') }}
    WHERE shipping_mode IS NOT NULL 
      AND delivery_status IS NOT NULL
)

SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY occurrences DESC) as shipping_id,
    
    shipping_mode,
    delivery_status,
    
    -- Classification du mode
    CASE 
        WHEN shipping_mode LIKE '%Same Day%' THEN 'Express'
        WHEN shipping_mode LIKE '%First Class%' THEN 'Priority'
        WHEN shipping_mode LIKE '%Second Class%' THEN 'Standard'
        WHEN shipping_mode LIKE '%Standard%' THEN 'Economy'
        ELSE 'Other'
    END as shipping_class,
    
    -- Statut simplifié
    CASE
        WHEN delivery_status = 'Shipping on time' THEN 'On Time'
        WHEN delivery_status = 'Advance shipping' THEN 'Early'
        WHEN delivery_status = 'Late delivery' THEN 'Late'
        WHEN delivery_status = 'Shipping canceled' THEN 'Canceled'
        ELSE 'Unknown'
    END as delivery_status_simple,
    
    -- Métriques
    occurrences as total_shipments,
    ROUND(CAST(avg_actual_days AS NUMERIC), 2) as avg_delivery_days,
    ROUND(CAST(avg_scheduled_days AS NUMERIC), 2) as avg_scheduled_days,
    ROUND(CAST(avg_delay_days AS NUMERIC), 2) as avg_delay_days,
    ROUND(CAST(late_risk_rate * 100 AS NUMERIC), 2) as late_risk_rate_pct

FROM shipping_combinations
ORDER BY occurrences DESC
