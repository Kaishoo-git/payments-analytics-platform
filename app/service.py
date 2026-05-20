from sqlalchemy.orm import Session

from app.schema import PaymentCreate
from app.db.models.model import Payment, Transaction
from app.repository import PaymentRepository, TransactionRepository


class PaymentService:
    def create_payment(self, db: Session, paymentCreate: PaymentCreate):
        new_payment = Payment(
            merchant_id=paymentCreate.merchant_id,
            card_pan=paymentCreate.card_pan,
            amount=paymentCreate.amount,
            status="CREATED",
        )
        PaymentRepository().create_payment(db, new_payment)
        return new_payment

    def authorise_payment(self, db: Session, payment_id: int):
        payment = PaymentRepository().get_payment(db, payment_id)
        payment.status = "AUTHORISED" if payment.amount > 200 else "UNAUTHORISED"
        PaymentRepository().update_payment(db, payment)
        return payment.status
    
class TransactionService:
    def create_transaction(self, db: Session, payment_id: int, status: str):
        new_transaction = Transaction(
            payment_id=payment_id,
            status=status,
        )
        TransactionRepository().create_transaction(db, new_transaction)
        return new_transaction
