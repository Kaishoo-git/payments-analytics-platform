from fastapi import APIRouter
from app.services.fraud_service import calculate_fraud_score

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/transaction")
def create_transaction(payload: dict):

    fraud_score = calculate_fraud_score(
        payload["amount"],
        payload["country"]
    )

    return {
        "status": "processed",
        "fraud_score": fraud_score
    }