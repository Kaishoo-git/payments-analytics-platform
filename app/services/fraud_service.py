from app.core.logging import logger
from datetime import datetime, timedelta
from app.db.models import Transaction

from sqlalchemy.orm import Session


class FraudService:

    def evaluate(self, tx: Transaction, db: Session):
        score = 0
        score += self._base_score(tx)
        score += self._repeated_score(tx, db)
        score += self._merchant_score(tx)
        if score > 0.8:
            decision = "DECLINE"
        elif score > 0.5:
            decision = "REVIEW"
        else:
            decision = "APPROVE"
        return score, decision

    def _base_score(self, tx: Transaction):
        if tx.amount < 0:
            logger.error("Negative transaction amount detected")
            raise ValueError("Amount cannot be negative")
        if tx.amount > 5000:
            return 0.95
        return 0.10
    
    def _repeated_score(self, tx: Transaction, db: Session):
        window = datetime.utcnow() - timedelta(minutes=5)
        count = (
            db
            .query(Transaction)
            .filter(Transaction.user_id == tx.user_id)
            .filter(Transaction.merchant_id >= tx.merchant_id)
            .filter(Transaction.created_at >= window)
            .count()
        )
        if count > 5:
            return 0.4
        return 0.0
    
    def _merchant_score(self, tx: Transaction):
        # To be Implemented
        return 0