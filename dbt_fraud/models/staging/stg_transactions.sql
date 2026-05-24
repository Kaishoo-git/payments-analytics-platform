SELECT
    ID AS transaction_id,
    PAYMENT_ID AS payment_id,
    STATUS AS transaction_status,
    CREATED_AT AS transaction_created_at
FROM {{ source('raw', 'TRANSACTIONS') }}