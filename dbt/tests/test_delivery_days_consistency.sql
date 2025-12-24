-- Test : Vérifier la cohérence des délais de livraison
SELECT
    order_id,
    days_for_shipping_real,
    days_for_shipment_scheduled
FROM {{ ref('stg_orders') }}
WHERE days_for_shipping_real < 0 
   OR days_for_shipment_scheduled < 0
