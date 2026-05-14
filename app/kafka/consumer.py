import json
from aiokafka import AIOKafkaConsumer

from app.kafka.topics import TRANSACTION_CREATED, FRAUD_SCORE_GENERATED
from app.kafka.producer import (
    publish,
    start_producer,
    stop_producer,
)


def calculate_fraud_score(event: dict) -> float:
    amount = event.get("amount", 0)
    if amount > 1000:
        return 0.9
    elif amount > 500:
        return 0.6
    return 0.1


async def consume_transactions():
    await start_producer()
    consumer = AIOKafkaConsumer(
        TRANSACTION_CREATED,
        bootstrap_servers="localhost:9092",
        group_id="fraud-service",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    print("Fraud consumer started")

    try:
        async for message in consumer:
            event = message.value
            print(f"Received: {event}")
            score = calculate_fraud_score(event)
            flagged = score > 0.8
            await publish(
                FRAUD_SCORE_GENERATED,
                {
                    "transaction_id": event["transaction_id"],
                    "user_id": event["user_id"],
                    "amount": event["amount"],
                    "risk_score": score,
                    "flagged": flagged,
                },
            )

    except Exception as e:
        print(f"Consumer error: {e}")

    finally:
        await consumer.stop()
        await stop_producer()
        print("Fraud consumer stopped")