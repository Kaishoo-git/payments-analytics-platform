from datetime import datetime
from pydantic import BaseModel, field_validator


class TransactionCreate(BaseModel):
    user_id: str
    wallet_id: str
    merchant_id: str
    amount: float
    currency: str

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: float):
        if amount < 0:
            raise ValueError("Amount must be positive")
        if amount > 1000000:
            raise ValueError("Amount cannot exceed 1000000")
        return amount

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, currency: str):
        if currency != currency.upper():
            raise ValueError("Currency must be uppercase")
        return currency


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