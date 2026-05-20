from datetime import datetime
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    merchant_id: int
    card_pan: str
    amount: float