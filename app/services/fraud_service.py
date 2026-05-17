from sqlalchemy.orm import Session

from app.db.models import TransactionStatus
from app.repositories.transaction_repository import TransactionRepository
from app.core.exceptions import TransactionNotFoundException
from app.db.models.transaction_model import FraudScore

class FraudService:

    def calculate_fraud_score(self, db: Session, event: dict):
        amount = event.get("amount", 0)
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        fraud_score = (
            0.95 if amount > 5000 else 0.1
            + self._user_enrichment_score(db, event.get("user_id"))
            + self._merchant_enrichment_score(db, event.get("merchant_id"))
        )
        wallet_amount = self._wallet_balance(db, event.get("wallet_id"))
        if fraud_score > 0.8:
            flagged = True
            decision = TransactionStatus.DENIED.value
        elif fraud_score > 0.5:
            flagged = True
            decision = TransactionStatus.REVIEW.value
        else:
            flagged = False
            decision = TransactionStatus.APPROVE.value
        if wallet_amount < amount:
            decision = TransactionStatus.DENIED.value
        return fraud_score, decision, flagged

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
    
    def _wallet_balance(self, db: Session, wallet_id: str):
        repository = TransactionRepository()
        wallet = repository.get_wallet(db, wallet_id)
        if not wallet:
            return 0.0
        return wallet.balance

    def add_fraud_score(
            self,
            db: Session,
            transaction_id: int,
            score: float,
            decision: str,
            flagged: bool
        ):
        repository = TransactionRepository()
        transaction = repository.add_fraud_score(db, transaction_id, score, decision, flagged)
        if not transaction:
            raise TransactionNotFoundException(f"Transaction not found: {transaction_id}")
        return transaction