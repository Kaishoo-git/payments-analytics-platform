SELECT
    ID,
    PAYMENT_ID,
    STATUS,
    CREATED_AT
FROM {{ source('raw', 'TRANSACTIONS') }}