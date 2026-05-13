from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction_schema import TransactionCreate
from app.repositories.transaction_repository import TransactionRepository
from app.services.fraud_service import FraudService

router = APIRouter()


@router.post("/transactions")
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    fraud_service = FraudService()
    score, decision = fraud_service.evaluate(payload.amount)
    tx_data = payload.model_dump()
    
    tx_data["risk_score"] = score
    tx_data["status"] = decision

    repository = TransactionRepository()

    tx = repository.create(db, tx_data)

    return tx