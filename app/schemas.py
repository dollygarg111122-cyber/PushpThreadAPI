from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    phone_no: str | None = Field(default=None, max_length=15)


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SizeBase(BaseModel):
    size: str = Field(min_length=1, max_length=50)


class SizeCreate(SizeBase):
    pass


class SizeRead(SizeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductSizeRead(SizeRead):
    available_quantity: int = Field(ge=0)


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    description: str | None = None
    image: str | None = Field(default=None, max_length=255)
    supplier_id: int = Field(gt=0)


class ProductCreate(ProductBase):
    size_ids: list[int] = Field(default_factory=list)


class ProductRead(ProductBase):
    id: int
    supplier: SupplierRead
    sizes: list[ProductSizeRead]
    model_config = ConfigDict(from_attributes=True)


class MappingCreate(BaseModel):
    product_id: int = Field(gt=0)
    size_id: int = Field(gt=0)
    available_quantity: int = Field(default=1, ge=0)


class MappingRead(MappingCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CustomerOrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    phone_no: str = Field(min_length=1, max_length=15)
    product_id: int = Field(gt=0)
    size_id: int = Field(gt=0)


class CustomerOrderRead(CustomerOrderCreate):
    id: int
    order_date: datetime
    model_config = ConfigDict(from_attributes=True)
