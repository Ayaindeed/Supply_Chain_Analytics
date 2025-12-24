-- Test personnalisé : Vérifier qu'il n'y a pas de dates futures
SELECT
    order_id,
    order_date
FROM {{ ref('stg_orders') }}
WHERE order_date > CURRENT_DATE
