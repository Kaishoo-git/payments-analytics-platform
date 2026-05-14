from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logging import setup_logging
from app.api.router import api_router

from app.kafka.producer import start_producer, stop_producer


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    yield
    await stop_producer()


app = FastAPI(
    title="Fraud Analytics Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Fraud Analytics Platform Running"}