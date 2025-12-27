{{ config(materialized='view') }}

-- Vue sur les métriques des modèles ML

SELECT
    model_name,
    model_type,
    metric_name,
    metric_value,
    training_date,
    n_features,
    n_samples_train
FROM {{ source('analytics', 'ml_model_metrics') }}