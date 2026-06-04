SELECT
    ID,
    PAYMENT_ID,
    STATUS AS EVENT_TYPE,
    CREATED_AT
FROM {{ ref('stg_payment_events') }}