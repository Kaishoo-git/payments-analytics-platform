from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database.db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    amount = Column(Float)
    merchant = Column(String)
    country = Column(String)
    fraud_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)