from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schema import PaymentCreate
from app.service import PaymentService
from app.core.logging import logger

from app.kafka.producer import publish
from app.kafka.topics import (
    PAYMENT_CREATED,
    PAYMENT_AUTHORISED,
    PAYMENT_UNAUTHORISED,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
async def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating payment for merchant={payload.merchant_id}")
    payment = PaymentService().create_payment(db, payload)
    await publish(
        PAYMENT_CREATED,
        {
            "payment_id": payment.id,
            "status": payment.status,
        }
    )
    authorised = PaymentService().authorise_payment(db, payment.id)
    if authorised:
        await publish(
            PAYMENT_AUTHORISED,
            {
                "payment_id": payment.id,
                "status": payment.status,
            }
        )
    else:
        await publish(
            PAYMENT_UNAUTHORISED,
            {
                "payment_id": payment.id,
                "status": payment.status,
            }
        )