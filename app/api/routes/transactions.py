from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from app.core.logging import logger

from app.kafka.producer import publish
from app.kafka.topics import TRANSACTION_CREATED

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/")
async def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating transaction for user={payload.user_id}")
    transaction_service = TransactionService()
    tx = transaction_service.create_transaction(db, payload)
    await publish(
        TRANSACTION_CREATED,
        {
            "transaction_id": tx.id,
            "user_id": tx.user_id,
            "amount": tx.amount,
            "risk_score": tx.risk_score,
            "status": tx.status,
        }
    )
    return tx


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str, 
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService()
    transaction = transaction_service.get_transaction_by_id(db, transaction_id)
    return transaction