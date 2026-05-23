from pydantic import BaseModel


class PaymentCreate(BaseModel):
    merchant_id: int
    card_pan: str
    amount: float


class MerchantCreate(BaseModel):
    webhook_url: str


class UserCreate(BaseModel):
    name: str
    card_pan: str