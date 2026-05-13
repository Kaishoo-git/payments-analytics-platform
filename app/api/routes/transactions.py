from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from app.services.fraud_service import FraudService
from app.core.logging import logger
from app.core.exceptions import TransactionNotFoundException


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/")
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    fraud_service = FraudService()
    score, decision = fraud_service.evaluate(
        tx=payload,
        db=db
    )
    tx_data = payload.model_dump()
    tx_data["risk_score"] = score
    tx_data["status"] = decision

    repository = TransactionRepository()

    tx = repository.create(db, tx_data)
    logger.info(f"Creating transaction for user={payload.user_id}")
    return tx


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db)
):
    transaction = (
        db
        .query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )
    if not transaction:
        raise TransactionNotFoundException("Transaction not found")
    return transaction


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    print(skip, limit)
    transactions = (
        db
        .query(Transaction)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions