import asyncio
from app.kafka.consumer import consume_transactions

if __name__ == "__main__":
    asyncio.run(consume_transactions())