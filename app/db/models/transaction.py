from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    merchant_id = Column(String, nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)

    status = Column(String, default="PENDING")
    risk_score = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)