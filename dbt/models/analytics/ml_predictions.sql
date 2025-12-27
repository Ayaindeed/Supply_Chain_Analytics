{{ config(materialized='view') }}

-- Vue sur les prédictions ML
-- Cette vue expose les prédictions de demande et de risque de retard

SELECT
    order_id,
    order_item_id,
    order_date,
    sales AS actual_sales,
    predicted_sales,
    late_delivery_risk AS actual_late_risk,
    predicted_late_risk,
    predicted_late_risk_proba,
    -- Calcul d'erreurs
    predicted_sales - sales AS sales_prediction_error,
    CASE WHEN predicted_late_risk = late_delivery_risk THEN 1 ELSE 0 END AS late_risk_prediction_correct
FROM {{ source('analytics', 'ml_predictions') }}