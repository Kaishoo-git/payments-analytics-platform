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
    return resp.json()


def create_user(base_url: str, card_count: int):
    card_pans = [fake.credit_card_number(card_type=None) for _ in range(card_count)]
    payload = {"name": fake.name(), "card_pans": card_pans,}
    for card_pan in card_pans:
        payload = {"name": fake.name(), "card_pan": card_pan,}
        resp = requests.post(f"{base_url}/users/", json=payload)
    resp.raise_for_status()
    user = resp.json()
    user["card_pans"] = card_pans
    return user


def create_payment(base_url: str, merchant_id: int, user_id: int, card_pan: str):
    payload = {
        "merchant_id": merchant_id,
        "user_id": user_id,
        "card_pan": card_pan,
        "amount": round(random.uniform(10, 500), 2),
    }
    resp = requests.post(f"{base_url}/payments/", json=payload)
    resp.raise_for_status()
    payment = resp.json()
    print(
        f"Created payment id={payment.get('payment_id')} merchant_id={merchant_id} "
        f"user_id={user_id} card_pan={card_pan} amount={payload['amount']} "
        f"status={payment.get('status')}"
    )
    return payment


def parse_args():
    parser = argparse.ArgumentParser(
        description="Seed users, merchants and post periodic payments until the timer expires or the script is stopped."
    )
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL, e.g. http://localhost:8000")
    parser.add_argument("--merchant-count", type=int, default=10, help="Number of merchants to create")
    parser.add_argument("--user-count", type=int, default=10, help="Number of users to create")
    parser.add_argument("--min-cards", type=int, default=1, help="Minimum cards per user")
    parser.add_argument("--max-cards", type=int, default=3, help="Maximum cards per user")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between payment posts")
    parser.add_argument("--duration", type=int, default=600, help="Total run time in seconds")
    return parser.parse_args()


def main():
    args = parse_args()
    merchants = []
    users = []

    try:
        print(f"Creating {args.merchant_count} merchants via POST {args.base_url}/merchant/")
        for _ in range(args.merchant_count):
            merchants.append(create_merchant(args.base_url))
        print("Merchant creation complete.")

        print(f"Creating {args.user_count} users via POST {args.base_url}/users/")
        for _ in range(args.user_count):
            cards = random.randint(args.min_cards, args.max_cards)
            users.append(create_user(args.base_url, cards))
        print("User creation complete.")
    except KeyboardInterrupt:
        print("Interrupted during setup.")
        return
    except Exception as exc:
        print(f"Setup failed: {exc}")
        return

    if not merchants or not users:
        print("No merchants or users created, aborting.")
        return
    print(
        f"Beginning payment posting loop for {len(users)} users and {len(merchants)} merchants. "
        f"Will run for up to {args.duration} seconds. Press Ctrl+C to stop early."
    )
    end_time = time.monotonic() + args.duration
    try:
        while time.monotonic() < end_time:
            merchant = random.choice(merchants)
            user = random.choice(users)
            card_pan = random.choice(user["card_pans"])
            try:
                create_payment(args.base_url, merchant["merchant_id"], user["user_id"], card_pan)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                print(
                    f"Payment post failed for merchant {merchant['merchant_id']} "
                    f"user {user['user_id']}: {exc}"
                )

            remaining = end_time - time.monotonic()
            if remaining <= 0: break
            time.sleep(min(args.interval, remaining))
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        print("Payment seed run complete.")


if __name__ == "__main__":
    main()
