SELECT 
    ID,
    WEBHOOK_URL,
    CREATED_AT
FROM {{ ref('stg_merchants') }}