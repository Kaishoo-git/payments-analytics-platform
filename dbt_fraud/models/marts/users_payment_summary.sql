

-- Total Amount of money tried to move by each user.
-- We have the total amount, then % breakdown.
SELECT
    u.user_id,
    u.user_name,
    COUNT(p.payment_id) AS number_of_payments,
    SUM(p.payment_amount) AS total_amount,

    SUM (
        CASE
            WHEN p.payment_status in ('CAPTURED', 'AUTHORIZED')
            THEN p.payment_amount
            ELSE 0
        END
    ) / NULLIF(SUM(p.payment_amount), 0) AS pct_authorised_amount,

    SUM (
        CASE
            WHEN p.payment_status in ('CAPTURED', 'AUTHORIZED')
            THEN 1
            ELSE 0
        END
    )::FLOAT / NULLIF(COUNT(p.payment_id), 0) AS pct_authorised_payments

FROM {{ ref('stg_payments') }} p

LEFT JOIN {{ ref('stg_users') }} u
    ON p.card_pan = u.card_pan

GROUP BY 
    u.user_id, u.user_name
