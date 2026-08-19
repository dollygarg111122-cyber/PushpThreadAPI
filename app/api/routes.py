from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import CustomerOrder, Product, ProductSizeMapping, ProductSizeMaster, ProductSupplier
from app.schemas import (
    MappingCreate,
    MappingRead,
    CustomerOrderCreate,
    CustomerOrderRead,
    ProductCreate,
    ProductRead,
    ProductSizeRead,
    SizeCreate,
    SizeRead,
    SupplierCreate,
    SupplierRead,
)

router = APIRouter()


def product_query():
    return select(Product).options(
        selectinload(Product.supplier),
        selectinload(Product.size_mappings).selectinload(ProductSizeMapping.size_master),
    )


def to_product_read(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        name=product.name,
        price=product.price,
        description=product.description,
        image=product.image,
        supplier_id=product.supplier_id,
        supplier=product.supplier,
        sizes=[
            ProductSizeRead(
                id=mapping.size_master.id,
                size=mapping.size_master.size,
                available_quantity=mapping.available_quantity,
            )
            for mapping in product.size_mappings
            if mapping.available_quantity > 0
        ],
    )


@router.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return db.scalars(select(ProductSupplier).order_by(ProductSupplier.name)).all()


@router.post("/suppliers", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    supplier = ProductSupplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/sizes", response_model=list[SizeRead])
def list_sizes(db: Session = Depends(get_db)):
    return db.scalars(select(ProductSizeMaster).order_by(ProductSizeMaster.size)).all()


@router.post("/sizes", response_model=SizeRead, status_code=status.HTTP_201_CREATED)
def create_size(payload: SizeCreate, db: Session = Depends(get_db)):
    size = ProductSizeMaster(**payload.model_dump())
    db.add(size)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Size already exists")
    db.refresh(size)
    return size


@router.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return [to_product_read(product) for product in db.scalars(product_query()).unique().all()]


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.scalars(product_query().where(Product.id == product_id)).unique().one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_product_read(product)


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    supplier = db.get(ProductSupplier, payload.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=400, detail="Supplier not found")

    sizes = db.scalars(select(ProductSizeMaster).where(ProductSizeMaster.id.in_(payload.size_ids))).all()
    if len(sizes) != len(set(payload.size_ids)):
        raise HTTPException(status_code=400, detail="One or more sizes not found")

    product = Product(**payload.model_dump(exclude={"size_ids"}), supplier=supplier)
    product.size_mappings = [ProductSizeMapping(size_master=size) for size in sizes]
    db.add(product)
    db.commit()
    product = db.scalars(product_query().where(Product.id == product.id)).unique().one()
    return to_product_read(product)


@router.post("/product-size-mappings", response_model=MappingRead, status_code=status.HTTP_201_CREATED)
def create_mapping(payload: MappingCreate, db: Session = Depends(get_db)):
    if db.get(Product, payload.product_id) is None or db.get(ProductSizeMaster, payload.size_id) is None:
        raise HTTPException(status_code=400, detail="Product or size not found")
    mapping = ProductSizeMapping(**payload.model_dump())
    db.add(mapping)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product-size mapping already exists")
    db.refresh(mapping)
    return mapping


@router.post("/orders", response_model=CustomerOrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: CustomerOrderCreate, db: Session = Depends(get_db)):
    mapping = db.scalars(
        select(ProductSizeMapping)
        .where(
            ProductSizeMapping.product_id == payload.product_id,
            ProductSizeMapping.size_id == payload.size_id,
        )
        .with_for_update()
    ).one_or_none()
    if mapping is None:
        raise HTTPException(status_code=400, detail="Product-size combination not found")
    if mapping.available_quantity < 1:
        raise HTTPException(status_code=409, detail="Selected product size is out of stock")

    mapping.available_quantity -= 1
    order = CustomerOrder(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=list[CustomerOrderRead])
def list_orders(db: Session = Depends(get_db)):
    return db.scalars(select(CustomerOrder).order_by(CustomerOrder.order_date.desc())).all()
