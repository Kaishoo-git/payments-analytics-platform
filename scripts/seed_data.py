from faker import Faker
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.transaction_schema import TransactionCreate
from app.services.transaction_service import TransactionService

from sqlalchemy.orm import Session

Faker.seed(1)
fake = Faker()

def seed_users(db: Session):
    transaction_service = TransactionService()
    for _ in range(20):
        tx = TransactionCreate(
            user_id=fake.vin(),
            merchant_id=fake.company(),
            amount=fake.pyfloat(min_value=1, max_value=10000, right_digits=2),
            currency=fake.currency_code(),
        )
        transaction_service.create_transaction(db, tx)
    

def main():
    db = SessionLocal()
    try:
        print("Seeding database...")
        seed_users(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()