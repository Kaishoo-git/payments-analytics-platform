from sqlalchemy.orm import Session

from app.schemas.transaction_schema import TransactionCreate
from app.db.models import Transaction, TransactionStatus
from app.repositories.transaction_repository import TransactionRepository
from app.core.exceptions import TransactionNotFoundException


class WalletService:
    def update_wallet_balance(self, db: Session, wallet_id: str, amount: float):
        repository = TransactionRepository()
        wallet = repository.update_wallet_balance(db, wallet_id, amount)
        if not wallet:
            raise TransactionNotFoundException("Wallet not found")
        return wallet
    
