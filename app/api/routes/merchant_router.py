from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.logging import logger
from app.db.core import get_db
from app.schema import MerchantCreate
from app.service import MerchantService

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.post("/")
async def create_merchant(
    payload: MerchantCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating merchant with webhook URL={payload.webhook_url}")
    merchant_id, webhook_url = MerchantService().create_merchant(db, payload)
    return {"merchant_id": merchant_id, "webhook_url": webhook_url}