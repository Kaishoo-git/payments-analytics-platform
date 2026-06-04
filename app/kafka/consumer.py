import json
from aiokafka import AIOKafkaConsumer

from app.db.core import SessionLocal
from app.service import PaymentService
from app.kafka.topics import (
    PAYMENT_CAPTURED,
)
from app.kafka.producer import (
    start_producer,
    stop_producer,
    publish,
)
from app.core.logging import logger

def run_db_task(task):
    db = SessionLocal()
    try:
        result = task(db)
        db.commit()
        return result
    except Exception as e:
        logger.exception(f"Database task failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def consume_transactions():
    await start_producer()
    consumer = AIOKafkaConsumer(
        PAYMENT_CAPTURED,
        bootstrap_servers="kafka:9092",
        group_id="fraud-service",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for message in consumer:
            event, topic = message.value, message.topic
            logger.info(f"[Consumer] Received from {topic}: {event}")
            if topic == PAYMENT_CAPTURED:
                payment_id = event["payment_id"]
                webhook_url = run_db_task(
                    lambda db: PaymentService().send_merchant_webhook(db, payment_id)
                )
    except Exception as e:
        logger.exception(f"Consumer error: {e}")

    finally:
        await consumer.stop()
        await stop_producer()
        logger.info("Fraud consumer stopped")