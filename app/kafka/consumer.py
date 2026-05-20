import json
from aiokafka import AIOKafkaConsumer

from app.db.session import SessionLocal
from app.service import PaymentService, TransactionService
from app.kafka.topics import (
    PAYMENT_CREATED,
    PAYMENT_AUTHORISED,
    PAYMENT_UNAUTHORISED,
    PAYMENT_CAPTURED,
)
from app.kafka.producer import (
    start_producer,
    stop_producer,
    publish,
)


async def consume_transactions():
    await start_producer()
    consumer = AIOKafkaConsumer(
        PAYMENT_CREATED,
        PAYMENT_AUTHORISED,
        PAYMENT_UNAUTHORISED,
        PAYMENT_CAPTURED,
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
            event, topic = message.value, message.topic
            print(f"[Consumer] Received from {topic}: {event}")
            TransactionService().create_transaction(
                db=SessionLocal(),
                payment_id=event["payment_id"],
                status=event["status"]
            )
            if topic == PAYMENT_AUTHORISED:
                
                # We update the ledge with CAPTURED status for AUTHORISED payments
                await publish(
                    PAYMENT_CAPTURED,
                    {
                        "payment_id": event["payment_id"],
                        "status": "CAPTURED",
                    }
                )
    except Exception as e:
        print(f"Consumer error: {e}")

    finally:
        await consumer.stop()
        await stop_producer()
        print("Fraud consumer stopped")