import json
from aiokafka import AIOKafkaConsumer

from app.db.session import SessionLocal
from app.services.transaction_service import TransactionService
from app.services.fraud_service import FraudService
from app.services.wallet_service import WalletService
from app.kafka.topics import (
    TRANSACTION_CREATED,
    FRAUD_SCORE_GENERATED,
    TRANSACTION_APPROVED,
    TRANSACTION_REVIEW,
    TRANSACTION_DECLINED,
)
from app.kafka.producer import (
    start_producer,
    stop_producer,
    publish,
)


async def consume_transactions():
    await start_producer()
    consumer = AIOKafkaConsumer(
        TRANSACTION_CREATED,
        FRAUD_SCORE_GENERATED,
        TRANSACTION_APPROVED,
        TRANSACTION_REVIEW,
        TRANSACTION_DECLINED,
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
            topic = message.topic
            print(f"Received from {topic}: {event}")
            if topic == TRANSACTION_CREATED:
                db = SessionLocal()
                service = FraudService()
                fraud_score, decision, flagged = service.calculate_fraud_score(db, event)
                service.add_fraud_score(db, int(event["transaction_id"]), fraud_score, decision, flagged)
                await publish(
                    FRAUD_SCORE_GENERATED,
                    {
                        "transaction_id": event["transaction_id"],
                        "user_id": event["user_id"],
                        "amount": event["amount"],
                        "fraud_score": fraud_score,
                        "decision": decision,
                        "flagged": flagged,
                    },
                )
            elif topic == FRAUD_SCORE_GENERATED:
                status = event["decision"]
                if status == "APPROVE":
                    target_topic = TRANSACTION_APPROVED
                elif status == "REVIEW":
                    target_topic = TRANSACTION_REVIEW
                else:
                    target_topic = TRANSACTION_DECLINED
                await publish(
                    target_topic,
                    {
                        "transaction_id": event["transaction_id"],
                        "user_id": event["user_id"],
                        "amount": event["amount"],
                        "fraud_score": event["fraud_score"],
                        "decision": event["decision"],
                    },
                )
            elif topic == "TRANSACTION_APPROVED":
                db = SessionLocal()
                transaction_service = TransactionService()
                transaction_service.update_transaction_status(
                    db, 
                    int(event["transaction_id"]), 
                    event["decision"]
                )
                transaction_service.add_transaction_event(
                    db,
                    int(event["transaction_id"]),
                    event["decision"],
                    event["fraud_score"],
                )
                wallet_service = WalletService()
                wallet_service.update_wallet_balance(
                    db,
                    event["user_id"],
                    event["amount"],
                    event["currency"],
                )
                print(f"Approved transaction {event['transaction_id']} and updated wallet")

            elif topic in [TRANSACTION_REVIEW, TRANSACTION_DECLINED]:
                db = SessionLocal()
                service = TransactionService()
                service.update_transaction_status(
                    db, 
                    int(event["transaction_id"]), 
                    event["decision"]
                )
                service.add_transaction_event(
                    db,
                    int(event["transaction_id"]),
                    event["decision"],
                    event["fraud_score"],
                )
                print(f"Updated transaction {event['transaction_id']} to {event['decision']}")

    except Exception as e:
        print(f"Consumer error: {e}")

    finally:
        await consumer.stop()
        await stop_producer()
        print("Fraud consumer stopped")