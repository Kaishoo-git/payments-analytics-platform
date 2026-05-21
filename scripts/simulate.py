import argparse
import random
import time

import requests
from faker import Faker

BASE_URL = "http://app:8000"
Faker.seed(1)
fake = Faker()


def create_merchant(base_url: str):
    payload = {"webhook_url": fake.url()}
    resp = requests.post(f"{base_url}/merchant/", json=payload)
    resp.raise_for_status()
    merchant = resp.json()
    return merchant


def create_payment(base_url: str, merchant_id: int):
    payload = {
        "merchant_id": merchant_id,
        "card_pan": fake.credit_card_number(card_type=None),
        "amount": round(random.uniform(10, 500), 2),
    }
    resp = requests.post(f"{base_url}/payments/", json=payload)
    resp.raise_for_status()
    payment = resp.json()
    print(
        f"Created payment id={payment.get('payment_id')} merchant_id={merchant_id} "
        f"amount={payload['amount']} status={payment.get('status')}"
    )
    return payment


def parse_args():
    parser = argparse.ArgumentParser(
        description="Seed merchants and post periodic payments until the timer expires or the script is stopped."
    )
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL, e.g. http://localhost:8000")
    parser.add_argument("--merchant-count", type=int, default=10, help="Number of merchants to create")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between payment posts")
    parser.add_argument("--duration", type=int, default=600, help="Total run time in seconds")
    return parser.parse_args()


def main():
    args = parse_args()
    merchants = []

    try:
        print(f"Creating {args.merchant_count} merchants via POST {args.base_url}/merchant/")
        for _ in range(args.merchant_count):
            merchants.append(create_merchant(args.base_url))
        print(f"Done.")
    except KeyboardInterrupt:
        print("Interrupted during merchant creation.")
        return
    except Exception as exc:
        print(f"Merchant creation failed: {exc}")
        return

    if not merchants:
        print("No merchants created, aborting.")
        return

    print(
        f"Beginning payment posting loop for {len(merchants)} merchants. "
        f"Will run for up to {args.duration} seconds. Press Ctrl+C to stop early."
    )

    end_time = time.monotonic() + args.duration
    merchant_index = 0

    try:
        while time.monotonic() < end_time:
            merchant = merchants[merchant_index]
            try:
                create_payment(args.base_url, merchant["merchant_id"])
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(f"Payment post failed for merchant {merchant['merchant_id']}: {exc}")

            merchant_index = (merchant_index + 1) % len(merchants)
            remaining = end_time - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(args.interval, remaining))
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        print("Payment seed run complete.")


if __name__ == "__main__":
    main()
