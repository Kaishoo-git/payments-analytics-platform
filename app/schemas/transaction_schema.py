from datetime import datetime
from pydantic import BaseModel


class TransactionCreate(BaseModel):
    user_id: str
    wallet_id: str
    merchant_id: str
    amount: float
    currency: str


class TransactionResponse(BaseModel):
    id: int
    user_id: str
    wallet_id: str
    merchant_id: str
    amount: float
    currency: str
    status: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True