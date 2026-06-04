WITH payment_lifecycle AS (
    SELECT
        e.payment_id,
        p.merchant_id AS merchant_id,
        MIN(CASE WHEN e.event_type = 'AUTHORISED' THEN e.created_at END) AS auth_ts,
        MIN(CASE WHEN e.event_type = 'WEBHOOK_SENT' THEN e.created_at END) AS webhook_ts
    FROM {{ ref('fact_payment_events') }} e
    LEFT JOIN {{ ref('fact_payments') }} p
        ON e.payment_id = p.ID
    GROUP BY e.payment_id, p.merchant_id
)
SELECT
    merchant_id,
    COUNT(auth_ts) AS authorized_payments,
    COUNT(webhook_ts) AS successful_webhooks,
    ROUND(
        COUNT(webhook_ts) * 100.0 / NULLIF(COUNT(auth_ts), 0), 2
    ) AS webhook_completion_rate_pct,
    AVG(
        DATEDIFF('millisecond', auth_ts, webhook_ts)
    ) AS avg_webhook_latency_ms
FROM payment_lifecycle
GROUP BY merchant_id