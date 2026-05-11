from fastapi import FastAPI

from app.database.db import Base, engine
from app.routes.transactions import router as transaction_router

# Create FastAPI app
app = FastAPI(
    title="Fraud Analytics Platform",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(transaction_router)


@app.get("/")
def root():
    return {"message": "Fraud Analytics Platform Running"}