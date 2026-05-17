from sqlalchemy.orm import Session

from app.core.logging import logger
from app.schemas.transaction_schema import TransactionCreate
from app.db.models import Transaction, TransactionStatus
from app.repositories.transaction_repository import TransactionRepository
from app.core.exceptions import TransactionNotFoundException


class TransactionService:
    
    def _validate_status(self, status: str):
        valid_statuses = [item.value for item in TransactionStatus]
        if status not in valid_statuses:
            raise ValueError(f"Unsupported transaction status: {status}")

    def create_transaction(self, db: Session, tx: TransactionCreate):
        transaction_data = tx.model_dump()
        transaction_data["status"] = TransactionStatus.CREATED.value
        transaction = Transaction(**transaction_data)
        repository = TransactionRepository()
        result = repository.create(db, transaction)
        repository.create_event(
            db,
            result.id,
            TransactionStatus.CREATED.value,
            {
                "user_id": result.user_id,
                "wallet_id": result.wallet_id,
                "merchant_id": result.merchant_id,
                "amount": result.amount,
                "currency": result.currency,
            },
        )
        return result

    def update_transaction_status(self, db: Session, transaction_id: int, status: str):
        self._validate_status(status)
        repository = TransactionRepository()
        transaction = repository.update_status(db, transaction_id, status)
        if not transaction:
            raise TransactionNotFoundException("Transaction not found")
        return transaction

    def add_transaction_event(self, db: Session, transaction_id: int, event_type: str, event_payload: dict):
        self._validate_status(event_type)
        repository = TransactionRepository()
        transaction = repository.get_by_id(db, transaction_id)
        if not transaction:
            raise TransactionNotFoundException(transaction_id)
        return repository.create_event(db, transaction_id, event_type, event_payload)

    def get_transaction_by_id(self, db: Session, transaction_id: str):
        repository = TransactionRepository()
        transaction = repository.get_by_id(db, transaction_id)
        if not transaction:
            raise TransactionNotFoundException("Transaction not found")
        return transaction