SELECT
    ID AS user_id,
    CARD_PAN AS card_pan,
    CREATED_AT AS user_created_at,
    NAME AS user_name
FROM {{ source('raw', 'USERS') }}