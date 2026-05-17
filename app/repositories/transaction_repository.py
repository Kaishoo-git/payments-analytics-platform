from datetime import datetime, timedelta

from app.db.models.transaction_model import Transaction, TransactionEvent, User, Wallet, Merchant
from sqlalchemy.orm import Session

class TransactionRepository:

    def create(self, db: Session, tx: Transaction):
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    def create_event(self, db: Session, transaction_id: int, event_type: str, event_payload: dict):
        transaction_event = TransactionEvent(
            transaction_id=transaction_id,
            event_type=event_type,
            event_payload=event_payload,
        )
        db.add(transaction_event)
        db.commit()
        db.refresh(transaction_event)
        return transaction_event
    
    def get_by_id(self, db: Session, transaction_id: str):
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_user(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == user_id).first()

    def get_merchant(self, db: Session, merchant_id: str):
        return db.query(Merchant).filter(Merchant.id == merchant_id).first()

    def get_wallet(self, db: Session, wallet_id: str):
        return db.query(Wallet).filter(Wallet.id == wallet_id).first()
    
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
    
    def update_status(self, db: Session, transaction_id: int, status: str):
        transaction = (
            db
            .query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )
        if not transaction:
            return None
        transaction.status = status
        db.commit()
        db.refresh(transaction)
        return transaction