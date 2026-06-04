SELECT
    ID,
    MERCHANT_ID,
    MASKED_CARD_PAN,
    AMOUNT,
    STATUS,
    CREATED_AT
FROM {{ ref('stg_payments') }}