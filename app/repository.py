from datetime import datetime, timedelta
from app.db.models.model import (
    Payment,
    User,
    Merchant,
    Transaction,
)
from sqlalchemy.orm import Session


class PaymentRepository:
    def create_payment(self, db: Session, payment: Payment):
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    def get_payment(self, db: Session, payment_id: int):
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    def update_payment(self, db: Session, payment: Payment):
        db.merge(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
class TransactionRepository:
    def create_transaction(self, db: Session, transaction: Transaction):
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction