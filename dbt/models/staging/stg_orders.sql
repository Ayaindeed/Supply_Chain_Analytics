{{
    config(
        materialized='view',
        schema='staging'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw_data', 'supply_chain_raw') }}
),

cleaned_orders AS (
    SELECT
        -- Identifiants
        order_id,
        order_item_id,
        order_customer_id,
        customer_id,
        
        -- Dates
        CAST(order_date_dateorders AS DATE) AS order_date,
        
        -- Informations client
        customer_fname,
        customer_lname,
        customer_email,
        customer_city,
        customer_state,
        customer_country,
        customer_zipcode,
        customer_segment,
        
        -- Informations commande
        order_city,
        order_country,
        order_state,
        order_region,
        order_status,
        market,
        
        -- Informations produit
        product_name,
        product_card_id,
        product_category_id,
        category_name,
        product_price,
        product_status,
        
        -- Métriques financières
        CAST(sales AS NUMERIC(10,2)) AS sales,
        CAST(order_item_discount AS NUMERIC(10,2)) AS order_item_discount,
        CAST(order_item_discount_rate AS NUMERIC(5,4)) AS order_item_discount_rate,
        CAST(order_item_product_price AS NUMERIC(10,2)) AS order_item_product_price,
        CAST(order_item_profit_ratio AS NUMERIC(5,4)) AS order_item_profit_ratio,
        CAST(order_item_total AS NUMERIC(10,2)) AS order_item_total,
        CAST(order_profit_per_order AS NUMERIC(10,2)) AS order_profit_per_order,
        CAST(benefit_per_order AS NUMERIC(10,2)) AS benefit_per_order,
        CAST(sales_per_customer AS NUMERIC(10,2)) AS sales_per_customer,
        
        -- Métriques de livraison
        days_for_shipping_real,
        days_for_shipment_scheduled,
        delivery_status,
        late_delivery_risk,
        shipping_mode,
        
        -- Quantités
        order_item_quantity,
        
        -- Géolocalisation
        latitude_src,
        longitude_src,
        
        -- Département
        department_name,
        department_id

    FROM source_data
    WHERE order_id IS NOT NULL
      AND order_date_dateorders IS NOT NULL
)

SELECT * FROM cleaned_orders
