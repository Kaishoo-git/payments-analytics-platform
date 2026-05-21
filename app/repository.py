from datetime import datetime, timedelta
from app.db.models.model import (
    Payment,
    Merchant,
    Transaction,
)
from sqlalchemy.orm import Session

class PaymentRepository:
    def create_payment(self, db: Session, merchant_id: int, card_pan: str, amount: float, status: str):
        payment = Payment(
            merchant_id=merchant_id,
            card_pan=card_pan,
            amount=amount,
            status=status
        )
        db.add(payment)
        db.flush()
        db.refresh(payment)
        return payment.id
    
    def get_payment_amount(self, db: Session, payment_id: int):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        return payment.amount if payment else None

    def update_status(self, db: Session, payment_id: int, status: str):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.status = status
            db.flush()
            db.refresh(payment)
            return payment.id
        
    def get_merchant_webhook(self, db: Session, payment_id: int):
        result = (
            db.query(Merchant.webhook_url)
            .join(Payment, Merchant.id == Payment.merchant_id)
            .filter(Payment.id == payment_id)
            .first()
        )
        return result.webhook_url if result else None
    
class TransactionRepository:
    def create_transaction(self, db: Session, payment_id: int, status: str):
        transaction = Transaction(
            payment_id=payment_id,
            status=status
        )
        db.add(transaction)
        db.flush()
        db.refresh(transaction)
        return transaction.id
    
class MerchantRepository:
    def create_merchant(self, db: Session, webhook_url: str):
        merchant = Merchant(webhook_url=webhook_url)
        db.add(merchant)
        db.flush()
        db.refresh(merchant)
        return merchant.id
    
class OutboxRepository:
    def add_event(self, db, event_type, payload):
        event = Outbox(
            event_type=event_type,
            payload=payload,
            published=False
        )
        db.add(event)