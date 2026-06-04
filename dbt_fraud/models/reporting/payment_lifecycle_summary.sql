WITH payment_events AS (
    SELECT
        payment_id,
        event_type,
        created_at AS event_timestamp
    FROM {{ ref('fact_payment_events') }}
)
SELECT
    payment_id,
    MIN(CASE WHEN event_type = 'CREATED' THEN event_timestamp END) AS created_ts,
    MIN(CASE WHEN event_type IN ('AUTHORIZED', 'UNAUTHORISED') THEN event_timestamp END) AS auth_ts,
    MIN(CASE WHEN event_type = 'CAPTURED' THEN event_timestamp END) AS capture_ts,
    MIN(CASE WHEN event_type = 'WEBHOOK_SENT' THEN event_timestamp END) AS webhook_ts,
    DATEDIFF(
        'second',
        MIN(CASE WHEN event_type = 'CREATED' THEN event_timestamp END),
        MAX(CASE WHEN event_type != 'CREATED' THEN event_timestamp END)
    ) AS total_lifecycle_secs,
    CASE
        WHEN MAX(CASE WHEN event_type IN ('WEBHOOK_SENT', 'UNAUTHORISED') THEN 1 ELSE 0 END) = 1 THEN 'COMPLETED'
        ELSE 'INCOMPLETE'
    END
    AS lifecycle_status_completed
FROM payment_events
GROUP BY payment_id