WITH latest_transactions AS (
    SELECT *
    FROM (
        SELECT
            transaction_id,
            payment_id,
            transaction_status,
            transaction_created_at,
            ROW_NUMBER() OVER (
                PARTITION BY payment_id
                ORDER BY transaction_created_at DESC
            ) AS rn
        FROM {{ ref('stg_transactions') }}
    )
    WHERE rn = 1
),

users AS (
    SELECT
        user_id,
        user_name,
        card_pan
    FROM {{ ref('stg_users') }}
),

merchants AS (
    SELECT
        merchant_id,
        merchant_webhook_url
    FROM {{ ref('stg_merchants') }}
)

SELECT
    p.payment_id AS payment_id,
    p.merchant_id AS merchant_id,
    CURRENT_TIMESTAMP() AS reconciliation_checked_at,
    p.card_pan AS card_pan,
    p.payment_amount AS payment_amount,
    p.payment_status AS payment_status,
    p.payment_created_at AS payment_created_at,
    CASE
        WHEN t.transaction_id IS NULL
            THEN 'MISSING_TRANSACTION'
        WHEN t.transaction_status != p.payment_status
            THEN 'STATUS_MISMATCH'
        WHEN t.transaction_created_at < p.payment_created_at
            THEN 'TIMING_ISSUE'
        WHEN m.merchant_id IS NULL
            THEN 'MISSING_MERCHANT'
        WHEN u.user_id IS NULL
            THEN 'UNKNOWN_USER'
        ELSE 'RECONCILED'
    END AS reconciliation_status

FROM {{ ref('stg_payments') }} p

LEFT JOIN latest_transactions t
    ON p.payment_id = t.payment_id

LEFT JOIN users u
    ON p.card_pan = u.card_pan

LEFT JOIN merchants m
    ON p.merchant_id = m.merchant_id