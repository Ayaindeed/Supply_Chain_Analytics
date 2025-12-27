-- Test that ML predictions table has data
SELECT
    COUNT(*) AS total_predictions
FROM {{ source('analytics', 'ml_predictions') }}
HAVING COUNT(*) = 0