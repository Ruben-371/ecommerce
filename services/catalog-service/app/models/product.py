"""Pydantic schemas for the Product resource."""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    sku: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    category: str = Field(default="general", max_length=100)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str

    model_config = {"from_attributes": True}
