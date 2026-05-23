from sqlalchemy.orm import Session

from app.schema import PaymentCreate, MerchantCreate, UserCreate
from app.repository import PaymentRepository, TransactionRepository, MerchantRepository, UserRepository


class PaymentService:
    def create_payment(self, db: Session, paymentCreate: PaymentCreate):
        payment_id = PaymentRepository().create_payment(
            db,
            merchant_id=paymentCreate.merchant_id,
            card_pan=paymentCreate.card_pan,
            amount=paymentCreate.amount,
            status="CREATED",
        )
        return payment_id

    def authorise_payment(self, db: Session, payment_id: int):
        payment_amount = PaymentRepository().get_payment_amount(db, payment_id)
        if payment_amount:
            status = "AUTHORISED" if payment_amount < 200 else "UNAUTHORISED"
            payment_id = PaymentRepository().update_status(db, payment_id, status)
            return status if payment_id else None
    
    def capture_payment(self, db: Session, payment_id: int):
        return PaymentRepository().update_status(
            db, payment_id, "CAPTURED"
        )
    
    def get_merchant_webhook(self, db: Session, payment_id: int):
        return PaymentRepository().get_merchant_webhook(db, payment_id)
    
    
class TransactionService:
    def create_transaction(self, db: Session, payment_id: int, status: str):
        return TransactionRepository().create_transaction(
            db, 
            payment_id=payment_id,
            status=status
        )
    
class MerchantService:
    def create_merchant(self, db: Session, merchantCreate: MerchantCreate):
        merchant_id = MerchantRepository().create_merchant(
            db, 
            webhook_url=merchantCreate.webhook_url
        )
        return merchant_id, merchantCreate.webhook_url


class UserService:
    def create_user(self, db: Session, userCreate: UserCreate):
        user_id = UserRepository().create_user(
            db,
            name=userCreate.name,
            card_pan=userCreate.card_pan,
        )
        return user_id