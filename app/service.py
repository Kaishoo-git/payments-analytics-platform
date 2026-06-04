from sqlalchemy.orm import Session

from app.schema import PaymentCreate, MerchantCreate, UserCreate
from app.repository import PaymentRepository, TransactionRepository, MerchantRepository, UserRepository

from app.core.logging import logger

class PaymentService:
    def create_payment(self, db: Session, paymentCreate: PaymentCreate):
        try:
            payment_id = PaymentRepository().create_payment(
                db,
                merchant_id=paymentCreate.merchant_id,
                card_pan=paymentCreate.card_pan,
                amount=paymentCreate.amount,
                status="CREATED",
            )
            (
                TransactionRepository()
                .create_transaction(db, payment_id=payment_id, status="CREATED")
            )
            db.commit()
            logger.info(
                f"Created payment with id={payment_id} for "
                f"merchant_id={paymentCreate.merchant_id} and amount={paymentCreate.amount}"
            )
            return payment_id
        except Exception as e:
            db.rollback()
            logger.exception(
                (
                    "Failed to create payment | "
                    f"merchant_id={paymentCreate.merchant_id} | "
                    f"amount={paymentCreate.amount}"
                )
            )
            raise

    def authorise_payment(self, db: Session, payment_id: int):
        try:
            payment_amount = PaymentRepository().get_payment_amount(db, payment_id)
            if payment_amount:
                status = "AUTHORISED" if payment_amount < 200 else "UNAUTHORISED"
                payment_id = PaymentRepository().update_status(db, payment_id, status)
                (
                    TransactionRepository()
                    .create_transaction(db, payment_id=payment_id, status=status)
                )
                if payment_id is None:
                    raise Exception("Payment not found")
                logger.info(f"Authorised payment with id={payment_id} and status={status}")
                db.commit()
                return status
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to authorise payment | payment_id={payment_id}")
            raise
    
    def capture_payment(self, db: Session, payment_id: int):
        try:
            (
                PaymentRepository()
                .update_status(db, payment_id, "CAPTURED")
            )
            (
                TransactionRepository()
                .create_transaction(db, payment_id=payment_id, status="CAPTURED")
            )
            db.commit()
            logger.info(f"Captured payment with id={payment_id}")
            return payment_id
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to capture payment | payment_id={payment_id}")
            raise

    def send_merchant_webhook(self, db: Session, payment_id: int):
        try:
            webhook_url = PaymentRepository().get_merchant_webhook(db, payment_id)
            if webhook_url is None:
                logger.warning(f"No webhook URL found for payment_id={payment_id}")
                raise ValueError("No webhook URL found")
            TransactionRepository().create_transaction(db, payment_id=payment_id, status="WEBHOOK_SENT")
            db.commit()
            logger.info(f"Sending webhook for payment_id={payment_id} to webhook_url={webhook_url}")
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to send merchant webhook for payment_id={payment_id}: {e}")
            raise


class MerchantService:
    def create_merchant(self, db: Session, merchantCreate: MerchantCreate):
        try:
            merchant_id = MerchantRepository().create_merchant(
                db, 
                webhook_url=merchantCreate.webhook_url
            )
            db.commit()
            logger.info(f"Created merchant with id={merchant_id} and webhook_url={merchantCreate.webhook_url}")
            return merchant_id, merchantCreate.webhook_url
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to create merchant | webhook_url={merchantCreate.webhook_url}")
            raise


class UserService:
    def create_user(self, db: Session, userCreate: UserCreate):
        try:
            user_id = UserRepository().create_user(
                db,
                name=userCreate.name,
                card_pan=userCreate.card_pan,
            )
            db.commit()
            logger.info(f"Created user with id={user_id} and name={userCreate.name}")
            return user_id
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to create user | name={userCreate.name}")
            raise