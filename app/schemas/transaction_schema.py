from pydantic import BaseModel

class TransactionCreate(BaseModel):
    user_id: str
    merchant_id: str
    amount: float
    currency: str


class TransactionResponse(BaseModel):
    id: int
    status: str
    risk_score: float

    class Config:
        from_attributes = True