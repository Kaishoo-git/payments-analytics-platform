SELECT 
    ID AS payment_id,
    MERCHANT_ID AS merchant_id,
    CARD_PAN AS card_pan,
    AMOUNT AS payment_amount,
    STATUS AS payment_status,
    CREATED_AT AS payment_created_at
FROM {{ source('raw', 'PAYMENTS') }}