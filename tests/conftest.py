import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine with in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def transaction_service(db_session):
    """Transaction service fixture."""
    from app.services.transaction_service import TransactionService
    return TransactionService()


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "user_id": "test_user_123",
        "wallet_id": "test_wallet_123",
        "merchant_id": "test_merchant",
        "amount": 100.50,
        "currency": "USD"
    }