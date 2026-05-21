import json
import os
from aiokafka import AIOKafkaProducer

producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    print(f"Kafka producer started (connecting to kafka:9092)")


async def stop_producer():
    global producer
    if producer:
        await producer.stop()
        print("Kafka producer stopped")


async def publish(topic: str, message: dict):
    if not producer:
        raise Exception("Producer not started")
    await producer.send_and_wait(topic, message)