"""Async MongoDB connection using Motor."""

import motor.motor_asyncio
from app.core.config import settings

_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
_db: motor.motor_asyncio.AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global _client, _db
    _client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    _db = _client[settings.DB_NAME]
    # Ensure indexes
    await _db["products"].create_index("sku", unique=True)
    print("MongoDB connected")


async def close_db() -> None:
    if _client:
        _client.close()


def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialised. Call connect_db() first.")
    return _db
