from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.core import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check_db(db: Session = Depends(get_db)):
    return {"status": "ok"}