from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.core import get_db
from app.schema import UserCreate
from app.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    user_id = UserService().create_user(db, payload)
    return {"user_id": user_id}