from fastapi import APIRouter

from app.api.routes import health_router, merchant_router, payment_router
from app.api.routes import health_router

api_router = APIRouter()

api_router.include_router(payment_router.router)
api_router.include_router(merchant_router.router)
api_router.include_router(health_router.router)