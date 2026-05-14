class TransactionNotFoundException(Exception):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        self.message = (
            f"Transaction {transaction_id} not found"
        )
        super().__init__(self.message)