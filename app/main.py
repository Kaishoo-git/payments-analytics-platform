from fastapi import FastAPI

from app.db.session import Base, engine
import app.db.models
from app.api.router import api_router
from sqlalchemy import inspect

# Create FastAPI app
app = FastAPI(
    title="Fraud Analytics Platform",
    version="1.0.0"
)

inspector = inspect(engine)
print("TABLES:", inspector.get_table_names())

# Register routes
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Fraud Analytics Platform Running"}