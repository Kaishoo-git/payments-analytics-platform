import json
import random
import urllib.request
import urllib.error
import urllib.parse
from typing import List

from faker import Faker
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.model import Wallet, Merchant

fake = Faker()
API_URL = "http://127.0.0.1:8000/transactions/"


def load_reference_data(db: Session):
    wallets = db.query(Wallet).all()
    merchants = db.query(Merchant).all()
    if not wallets or not merchants:
        raise RuntimeError(
            "No seeded wallets or merchants found. Run scripts/seed_data.py first."
        )
    return wallets, merchants


def build_transaction_payload(wallet: Wallet, merchant: Merchant):
    amount = round(random.uniform(1, 12000), 2)
    return {
        "user_id": wallet.user_id,
        "wallet_id": wallet.id,
        "merchant_id": merchant.id,
        "amount": amount,
        "currency": wallet.currency,
    }


def post_transaction(payload: dict):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.status, response.read().decode("utf-8")


def main(count: int = 10):
    db = SessionLocal()
    try:
        wallets, merchants = load_reference_data(db)
        print(f"Posting {count} transactions to {API_URL}")

        for i in range(count):
            wallet = random.choice(wallets)
            merchant = random.choice(merchants)
            payload = build_transaction_payload(wallet, merchant)
            try:
                status, body = post_transaction(payload)
                print(f"{i+1}/{count} posted {payload['amount']} for user={payload['user_id']} -> {status}")
            except urllib.error.HTTPError as exc:
                print(f"{i+1}/{count} failed: HTTP {exc.code} - {exc.read().decode('utf-8')}" )
            except Exception as exc:
                print(f"{i+1}/{count} failed: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()