from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.core import get_db
from app.schema import PaymentCreate
from app.service import PaymentService
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
    payment_id = PaymentService().create_payment(db, payload)
    status = PaymentService().authorise_payment(db, payment_id)
    if status == "AUTHORISED":
        payment_id = PaymentService().capture_payment(db, payment_id)
        await publish(PAYMENT_CAPTURED, {"payment_id": payment_id, "status": "CAPTURED"})
    return {"payment_id": payment_id, "status": status}