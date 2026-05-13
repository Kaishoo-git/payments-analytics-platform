from app.db.models.transaction import Transaction

class TransactionRepository:

    def create(self, db, transaction_data):
        tx = Transaction(**transaction_data)

        db.add(tx)
        db.commit()
        db.refresh(tx)

        return tx