from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models.model import User, Wallet, Merchant

Faker.seed(1)
fake = Faker()


def seed_users_wallets_merchants(db: Session, user_count: int = 10, merchant_count: int = 6):
    users = []
    wallets = []
    merchants = []

    for _ in range(user_count):
        user = User(
            id=fake.uuid4(),
            name=fake.name(),
            country=fake.country_code(),
            email=fake.unique.email(),
            risk_score=round(fake.pyfloat(min_value=0, max_value=1, right_digits=2), 2),
        )
        wallet = Wallet(
            id=fake.uuid4(),
            user_id=user.id,
            balance=round(fake.pyfloat(min_value=100, max_value=20000, right_digits=2), 2),
            currency=fake.currency_code(),
        )
        users.append(user)
        wallets.append(wallet)

    merchant_categories = ["electronics", "gaming", "travel", "crypto", "fashion", "groceries"]
    for _ in range(merchant_count):
        merchant = Merchant(
            id=fake.uuid4(),
            name=fake.company(),
            category=fake.random_element(merchant_categories),
        )
        merchants.append(merchant)

    db.add_all(users + wallets + merchants)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        print("Seed failed because of duplicate keys; rerun after cleaning the database.")
        raise


def main():
    db = SessionLocal()
    try:
        print("Seeding users, wallets, and merchants...")
        seed_users_wallets_merchants(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()