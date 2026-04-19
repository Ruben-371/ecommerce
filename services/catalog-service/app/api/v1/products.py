"""Products CRUD endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.core.database import get_db
from app.models.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 20, db=Depends(get_db)):
    limit = min(limit, 100)
    cursor = db["products"].find({"is_active": True}).skip(skip).limit(limit)
    return [_serialize(doc) async for doc in cursor]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    doc = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(doc)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db=Depends(get_db)):
    data = payload.model_dump()
    data["price"] = float(data["price"])
    result = await db["products"].insert_one(data)
    created = await db["products"].find_one({"_id": result.inserted_id})
    return _serialize(created)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, payload: ProductUpdate, db=Depends(get_db)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "price" in updates:
        updates["price"] = float(updates["price"])
    result = await db["products"].find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(result)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    result = await db["products"].delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
