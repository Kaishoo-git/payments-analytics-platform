from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.core import get_db
from app.schema import PaymentCreate
from app.service import PaymentService, TransactionService
from app.core.logging import logger

from app.kafka.producer import publish
from app.kafka.topics import (
    PAYMENT_CAPTURED,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
async def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating payment for merchant={payload.merchant_id}")
    payment_id = PaymentService().create_payment(db, payload)
    transaction_id = TransactionService().create_transaction(db, payment_id, "CREATED")
    status = PaymentService().authorise_payment(db, payment_id)
    transaction_id = TransactionService().create_transaction(db, payment_id, status)
    if status == "AUTHORISED":
        payment_id = PaymentService().capture_payment(db, payment_id)
        transaction_id = TransactionService().create_transaction(db, payment_id, "CAPTURED")
        await publish(PAYMENT_CAPTURED, {"payment_id": payment_id, "status": "CAPTURED"})
        
    return {"payment_id": payment_id, "status": status}