from sqlalchemy.orm import Session

from app.core.logging import logger
from app.schemas.transaction_schema import TransactionCreate
from app.db.models import Transaction, TransactionStatus
from app.repositories.transaction_repository import TransactionRepository
from app.core.exceptions import TransactionNotFoundException


class TransactionService:

    def calculate_fraud_score(self, db: Session, event: dict):
        amount = event.get("amount", 0)
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        base_score = 0.95 if amount > 5000 else 0.1
        enrichment = (
            self._user_enrichment_score(db, event.get("user_id"))
            + self._merchant_enrichment_score(db, event.get("merchant_id"))
            + self._wallet_enrichment_score(db, event.get("wallet_id"), amount)
        )

        fraud_score = min(base_score + enrichment, 1.0)
        if fraud_score > 0.8:
            decision = TransactionStatus.DENIED.value
        elif fraud_score > 0.5:
            decision = TransactionStatus.REVIEW.value
        else:
            decision = TransactionStatus.APPROVE.value
        return fraud_score, decision

    def _user_enrichment_score(self, db: Session, user_id: str):
        repository = TransactionRepository()
        user = repository.get_user(db, user_id)
        if not user:
            return 0.0
        score = 0.0
        if user.risk_score and user.risk_score > 0.5:
            score += min(user.risk_score / 2, 0.25)
        if user.country and user.country.upper() in {"NG", "UA", "PK", "RU"}:
            score += 0.15
        return score

    def _merchant_enrichment_score(self, db: Session, merchant_id: str):
        repository = TransactionRepository()
        merchant = repository.get_merchant(db, merchant_id)
        if not merchant:
            return 0.0
        high_risk_categories = {"gambling", "electronics", "adult", "crypto"}
        if merchant.category and merchant.category.lower() in high_risk_categories:
            return 0.2
        return 0.0

    def _wallet_enrichment_score(self, db: Session, wallet_id: str, amount: float):
        repository = TransactionRepository()
        wallet = repository.get_wallet(db, wallet_id)
        if not wallet:
            return 0.0
        score = 0.0
        if wallet.balance is not None and amount > wallet.balance * 0.5:
            score += 0.2
        if wallet.currency and wallet.currency != "USD":
            score += 0.05
        return score
    
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




    