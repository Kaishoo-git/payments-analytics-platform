from sqlalchemy.orm import Session

from app.core.logging import logger
from app.schemas.transaction_schema import TransactionCreate
from app.db.models import Transaction
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

        risk_score = min(base_score + enrichment, 1.0)
        if risk_score > 0.8:
            decision = "DECLINE"
        elif risk_score > 0.5:
            decision = "REVIEW"
        else:
            decision = "APPROVE"
        return decision, risk_score

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
        transaction_data = tx.model_dump()
        transaction_data["risk_score"] = risk_score
        transaction_data["status"] = "CREATED"
        transaction = Transaction(**transaction_data)
        repository = TransactionRepository()
        result = repository.create(db, transaction)
        return result

    def update_transaction_status(self, db: Session, transaction_id: int, status: str):
        repository = TransactionRepository()
        transaction = repository.update_status(db, transaction_id, status)
        if not transaction:
            raise TransactionNotFoundException("Transaction not found")
        return transaction

    def get_transaction_by_id(self, db: Session, transaction_id: str):
        repository = TransactionRepository()
        transaction = repository.get_by_id(db, transaction_id)
        if not transaction:
            raise TransactionNotFoundException("Transaction not found")
        return transaction




    