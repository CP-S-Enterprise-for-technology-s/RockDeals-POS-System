"""
CP'S Enterprise POS - Products API
===================================
Product management endpoints.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth import get_current_user
from src.core.exceptions import ConflictError, NotFoundError, ValidationError
from src.database import get_db
from src.models.product import Product
from src.models.user import User

router = APIRouter()


@router.get("/")
async def list_products(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query()] = None,
    category_id: Annotated[UUID | None, Query()] = None,
    low_stock: Annotated[bool | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = True,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List products with pagination and filtering.
    
    Args:
        page: Page number
        per_page: Items per page
        search: Search query for name or barcode
        category_id: Filter by category
        low_stock: Filter low stock products
        is_active: Filter by active status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of products
    """
    query = select(Product)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Product.name.ilike(search_filter)) |
            (Product.barcode.ilike(search_filter)) |
            (Product.sku.ilike(search_filter))
        )
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if low_stock:
        query = query.where(Product.stock_quantity <= Product.min_stock_level)
    
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    
    # Get total count
    count_result = await db.execute(select(Product).where(query.whereclause))
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "items": [product.to_dict(include_cost=current_user.is_manager) for product in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/search")
async def search_products(
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Quick search products.
    
    Args:
        q: Search query
        limit: Maximum results
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of matching products
    """
    search_filter = f"%{q}%"
    
    query = (
        select(Product)
        .where(
            (Product.name.ilike(search_filter)) |
            (Product.barcode.ilike(search_filter)) |
            (Product.sku.ilike(search_filter))
        )
        .where(Product.is_active == True)
        .limit(limit)
    )
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "items": [product.to_dict() for product in products],
        "total_results": len(products),
    }


@router.get("/low-stock")
async def get_low_stock_products(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get products with low stock.
    
    Args:
        page: Page number
        per_page: Items per page
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of low stock products
    """
    query = (
        select(Product)
        .where(Product.stock_quantity <= Product.min_stock_level)
        .where(Product.is_active == True)
    )
    
    # Get total count
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "items": [product.to_dict() for product in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new product.
    
    Args:
        data: Product creation data
        current_user: Current authenticated user (must be manager+)
        db: Database session
        
    Returns:
        Created product
    """
    # Check permissions
    if not current_user.is_manager:
        raise ValidationError("Only managers can create products")
    
    # Check if barcode exists
    if data.get("barcode"):
        result = await db.execute(
            select(Product).where(Product.barcode == data["barcode"])
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"Barcode '{data['barcode']}' already exists")
    
    # Check if SKU exists
    if data.get("sku"):
        result = await db.execute(
            select(Product).where(Product.sku == data["sku"])
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"SKU '{data['sku']}' already exists")
    
    # Create product
    product = Product(
        name=data["name"],
        barcode=data.get("barcode"),
        sku=data.get("sku"),
        description=data.get("description"),
        price=data["price"],
        cost=data.get("cost"),
        stock_quantity=data.get("stock_quantity", 0),
        min_stock_level=data.get("min_stock_level", 10),
        max_stock_level=data.get("max_stock_level"),
        category_id=data.get("category_id"),
        image_url=data.get("image_url"),
        is_active=data.get("is_active", True),
    )
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return product.to_dict(include_cost=True)


@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get product by ID.
    
    Args:
        product_id: Product ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Product data
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product", str(product_id))
    
    return product.to_dict(include_cost=current_user.is_manager)


@router.put("/{product_id}")
async def update_product(
    product_id: UUID,
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update product.
    
    Args:
        product_id: Product ID
        data: Product update data
        current_user: Current authenticated user (must be manager+)
        db: Database session
        
    Returns:
        Updated product
    """
    # Check permissions
    if not current_user.is_manager:
        raise ValidationError("Only managers can update products")
    
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product", str(product_id))
    
    # Check if barcode is being changed and if it already exists
    if data.get("barcode") and data["barcode"] != product.barcode:
        result = await db.execute(
            select(Product).where(Product.barcode == data["barcode"])
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"Barcode '{data['barcode']}' already exists")
        product.barcode = data["barcode"]
    
    # Check if SKU is being changed and if it already exists
    if data.get("sku") and data["sku"] != product.sku:
        result = await db.execute(
            select(Product).where(Product.sku == data["sku"])
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"SKU '{data['sku']}' already exists")
        product.sku = data["sku"]
    
    # Update fields
    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "price" in data:
        product.price = data["price"]
    if "cost" in data:
        product.cost = data["cost"]
    if "stock_quantity" in data:
        product.stock_quantity = data["stock_quantity"]
    if "min_stock_level" in data:
        product.min_stock_level = data["min_stock_level"]
    if "max_stock_level" in data:
        product.max_stock_level = data["max_stock_level"]
    if "category_id" in data:
        product.category_id = data["category_id"]
    if "image_url" in data:
        product.image_url = data["image_url"]
    if "is_active" in data:
        product.is_active = data["is_active"]
    
    await db.commit()
    await db.refresh(product)
    
    return product.to_dict(include_cost=True)


@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete product (soft delete).
    
    Args:
        product_id: Product ID
        current_user: Current authenticated user (must be admin)
        db: Database session
        
    Returns:
        Success message
    """
    # Check permissions
    if not current_user.is_admin:
        raise ValidationError("Only admins can delete products")
    
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise NotFoundError("Product", str(product_id))
    
    # Soft delete
    product.is_active = False
    await db.commit()
    
    return {"success": True, "message": "Product deleted successfully"}
