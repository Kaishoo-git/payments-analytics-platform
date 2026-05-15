from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.schemas.transaction_schema import TransactionCreate
from app.db.models import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.core.exceptions import TransactionNotFoundException


class TransactionService:

    def _base_score(self, tx: TransactionCreate):
        if tx.amount < 0:
            raise ValueError("Amount cannot be negative")
        return 0.95 if tx.amount > 5000 else 0.1

    def _repeated_score(self, tx: TransactionCreate, db: Session):
        repository = TransactionRepository()
        count = repository.count_transactions(db, tx)
        return 0.4 if count > 5 else 0.0
    
    def create_transaction(self, db: Session, tx: TransactionCreate):
        risk_score = 0
        risk_score += self._base_score(tx)
        risk_score += self._repeated_score(tx, db)
        if risk_score > 0.8:
            decision = "DECLINE"
        elif risk_score > 0.5:
            decision = "REVIEW"
        else:
            decision = "APPROVE"
        transaction_data = tx.model_dump()
        transaction_data["risk_score"] = risk_score
        transaction_data["status"]   = decision
        transaction = Transaction(**transaction_data)
        repository = TransactionRepository()
        result = repository.create(db, transaction)
        return result
    
    def get_transaction_by_id(self, db: Session, transaction_id: str):
        repository = TransactionRepository()
        transaction = repository.get_by_id(db, transaction_id)
        if not transaction:
            raise TransactionNotFoundException("Transaction not found")
        return transaction




    