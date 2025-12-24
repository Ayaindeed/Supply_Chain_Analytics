/*
    Dimension Date - Calendrier complet
    Permet les analyses temporelles avancées
*/

{{ config(
    materialized='table',
    schema='marts'
) }}

WITH date_spine AS (
    SELECT DISTINCT
        order_date_dateorders::date as date_value
    FROM {{ source('raw_data', 'supply_chain_raw') }}
    WHERE order_date_dateorders IS NOT NULL
),

date_attributes AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY date_value) as date_id,
        date_value,
        
        -- Composants de date
        EXTRACT(YEAR FROM date_value)::int as year,
        EXTRACT(QUARTER FROM date_value)::int as quarter,
        EXTRACT(MONTH FROM date_value)::int as month,
        EXTRACT(DAY FROM date_value)::int as day,
        EXTRACT(DOW FROM date_value)::int as day_of_week,
        EXTRACT(DOY FROM date_value)::int as day_of_year,
        EXTRACT(WEEK FROM date_value)::int as week_of_year,
        
        -- Attributs textuels
        TO_CHAR(date_value, 'Month') as month_name,
        TO_CHAR(date_value, 'Day') as day_name,
        TO_CHAR(date_value, 'YYYY-MM') as year_month,
        TO_CHAR(date_value, 'YYYY-Q') as year_quarter,
        
        -- Indicateurs
        CASE WHEN EXTRACT(DOW FROM date_value) IN (0, 6) THEN 1 ELSE 0 END as is_weekend,
        CASE WHEN EXTRACT(DAY FROM date_value) <= 5 THEN 1 ELSE 0 END as is_month_start,
        CASE WHEN EXTRACT(DAY FROM date_value) >= 25 THEN 1 ELSE 0 END as is_month_end,
        
        -- Période fiscale (exemple: année commence en janvier)
        CASE 
            WHEN EXTRACT(MONTH FROM date_value) >= 1 THEN EXTRACT(YEAR FROM date_value)
            ELSE EXTRACT(YEAR FROM date_value) - 1
        END as fiscal_year,
        
        -- Saison (pour analyses saisonnières)
        CASE 
            WHEN EXTRACT(MONTH FROM date_value) IN (12, 1, 2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM date_value) IN (3, 4, 5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM date_value) IN (6, 7, 8) THEN 'Summer'
            ELSE 'Fall'
        END as season
        
    FROM date_spine
)

SELECT * FROM date_attributes
ORDER BY date_value
