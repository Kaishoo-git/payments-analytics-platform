from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import TransactionNotFoundException
from app.core.logging import setup_logging

from app.db.session import Base, engine
from app.api.router import api_router

import app.db.models

setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Fraud Analytics Platform",
    version="1.0.0"
)

@app.exception_handler(TransactionNotFoundException)
async def transaction_not_found_handler(
    request: Request,
    exc: TransactionNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )

# Register routes
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Fraud Analytics Platform Running"}