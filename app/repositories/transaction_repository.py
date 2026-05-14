from datetime import datetime, timedelta

from app.db.models.transaction import Transaction
from sqlalchemy.orm import Session

class TransactionRepository:

    def create(self, db: Session, tx: Transaction):
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx
    
    def get_by_id(self, db: Session, transaction_id: str):
        transaction = (
            db
            .query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )
        return transaction
    
    def count_transactions(self, db: Session, tx: Transaction):
        window = datetime.utcnow() - timedelta(minutes=5)
        count = (
            db
            .query(Transaction)
            .filter(Transaction.user_id == tx.user_id)
            .filter(Transaction.created_at >= window)
            .count()
        )
        return count