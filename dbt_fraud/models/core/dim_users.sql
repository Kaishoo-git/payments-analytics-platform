SELECT
    ID,
    MASKED_CARD_PAN,
    CREATED_AT,
    NAME
FROM {{ ref('stg_users') }}