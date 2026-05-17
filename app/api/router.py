from fastapi import APIRouter

from app.api.routes import transaction_router
from app.api.routes import health_router

api_router = APIRouter()

api_router.include_router(transaction_router.router)
api_router.include_router(health_router.router)