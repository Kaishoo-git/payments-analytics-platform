SELECT 
    ID AS merchant_id,
    WEBHOOK_URL AS merchant_webhook_url,
    CREATED_AT AS merchant_created_at
FROM {{ source('raw', 'MERCHANTS') }}