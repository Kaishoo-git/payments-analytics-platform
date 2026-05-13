from fastapi import APIRouter

from app.api.routes import transactions
from app.api.routes import health

api_router = APIRouter()

api_router.include_router(transactions.router)
api_router.include_router(health.router)