import pytest
from app.schemas.transaction_schema import TransactionCreate
from app.services.transaction_service import TransactionService
from app.core.exceptions import TransactionNotFoundException


class TestTransactionService:

    def test_create_transaction_success(self, transaction_service, db_session, sample_transaction_data):
        """Test successful transaction creation."""
        tx_data = TransactionCreate(**sample_transaction_data)
        result = transaction_service.create_transaction(db_session, tx_data)

        assert result.user_id == sample_transaction_data["user_id"]
        assert result.amount == sample_transaction_data["amount"]
        assert result.status == "CREATED"
        assert 0 <= result.risk_score <= 1

    def test_create_transaction_negative_amount(self, transaction_service, db_session, sample_transaction_data):
        """Test transaction creation with negative amount fails."""
        invalid_data = sample_transaction_data.copy()
        invalid_data["amount"] = -100

        tx_data = TransactionCreate(**invalid_data)
        with pytest.raises(ValueError, match="Amount must be positive"):
            transaction_service.create_transaction(db_session, tx_data)

    def test_create_transaction_high_amount_risk(self, transaction_service, db_session, sample_transaction_data):
        """Test high amount transaction gets high risk score."""
        high_amount_data = sample_transaction_data.copy()
        high_amount_data["amount"] = 10000

        tx_data = TransactionCreate(**high_amount_data)
        result = transaction_service.create_transaction(db_session, tx_data)

        assert result.risk_score == 0.0
        assert result.status == "CREATED"

    def test_get_transaction_by_id_success(self, transaction_service, db_session, sample_transaction_data):
        """Test retrieving existing transaction."""
        # Create transaction first
        tx_data = TransactionCreate(**sample_transaction_data)
        created_tx = transaction_service.create_transaction(db_session, tx_data)

        # Retrieve it
        result = transaction_service.get_transaction_by_id(db_session, created_tx.id)

        assert result.id == created_tx.id
        assert result.user_id == sample_transaction_data["user_id"]

    def test_get_transaction_by_id_not_found(self, transaction_service, db_session):
        """Test retrieving non-existent transaction raises exception."""
        with pytest.raises(TransactionNotFoundException):
            transaction_service.get_transaction_by_id(db_session, 99999)


class TestTransactionValidation:

    def test_valid_transaction_creation(self):
        """Test valid transaction data passes validation."""
        data = {
            "user_id": "user123",
            "wallet_id": "wallet456",
            "merchant_id": "merchant456",
            "amount": 100.50,
            "currency": "USD"
        }
        tx = TransactionCreate(**data)
        assert tx.amount == 100.50
        assert tx.currency == "USD"

    def test_invalid_currency_format(self):
        """Test invalid currency format fails validation."""
        data = {
            "user_id": "user123",
            "wallet_id": "wallet456",
            "merchant_id": "merchant456",
            "amount": 100.50,
            "currency": "usd"  # lowercase should fail
        }
        with pytest.raises(ValueError):
            TransactionCreate(**data)

    def test_amount_too_high(self):
        """Test amount exceeding maximum fails validation."""
        data = {
            "user_id": "user123",
            "wallet_id": "wallet456",
            "merchant_id": "merchant456",
            "amount": 2000000,  # Exceeds 1M limit
            "currency": "USD"
        }
        with pytest.raises(ValueError, match="Amount cannot exceed"):
            TransactionCreate(**data)

    def test_zero_amount(self):
        """Test zero amount fails validation."""
        data = {
            "user_id": "user123",
            "wallet_id": "wallet456",
            "merchant_id": "merchant456",
            "amount": 0,
            "currency": "USD"
        }
        with pytest.raises(ValueError, match="Amount must be positive"):
            TransactionCreate(**data)