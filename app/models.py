from __future__ import annotations

from typing import List

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ProductSupplier(Base):
    __tablename__ = "ProductSupplier"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("Name", String(100), nullable=False)
    address: Mapped[str | None] = mapped_column("Address", String(255))
    phone_no: Mapped[str | None] = mapped_column("PhoneNo", String(15))

    products: Mapped[List[Product]] = relationship(back_populates="supplier")


class Product(Base):
    __tablename__ = "Product"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String(255))
    supplier_id: Mapped[int] = mapped_column("SupplierId", ForeignKey("ProductSupplier.ID"), nullable=False)

    supplier: Mapped[ProductSupplier] = relationship(back_populates="products")
    size_mappings: Mapped[List[ProductSizeMapping]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductSizeMaster(Base):
    __tablename__ = "ProductSizeMaster"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    size: Mapped[str] = mapped_column("Size", String(50), nullable=False, unique=True)

    product_mappings: Mapped[List[ProductSizeMapping]] = relationship(back_populates="size_master")


class ProductSizeMapping(Base):
    __tablename__ = "ProductSizeMapping"
    __table_args__ = (UniqueConstraint("ProductId", "SizeID", name="UQ_ProductSizeMapping_Product_Size"),)

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column("ProductId", ForeignKey("Product.id"), nullable=False)
    size_id: Mapped[int] = mapped_column("SizeID", ForeignKey("ProductSizeMaster.ID"), nullable=False)
    available_quantity: Mapped[int] = mapped_column("AvailableQuantity", Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="size_mappings")
    size_master: Mapped[ProductSizeMaster] = relationship(back_populates="product_mappings")


class CustomerOrder(Base):
    __tablename__ = "CustomerOrder"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column("CustomerName", String(100), nullable=False)
    phone_no: Mapped[str] = mapped_column("PhoneNo", String(15), nullable=False)
    product_id: Mapped[int] = mapped_column("ProductID", ForeignKey("Product.id"), nullable=False)
    size_id: Mapped[int] = mapped_column("SizeID", ForeignKey("ProductSizeMaster.ID"), nullable=False)
    order_date: Mapped[datetime] = mapped_column("Date", DateTime, nullable=False, default=datetime.now)

    product: Mapped[Product] = relationship()
    size_master: Mapped[ProductSizeMaster] = relationship()
