"""Catalog Service – product management with MongoDB."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_db, close_db
from app.api.v1 import products


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Catalog Service",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "catalog-service"}


app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
