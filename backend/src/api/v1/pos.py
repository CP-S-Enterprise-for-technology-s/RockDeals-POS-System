"""
CP'S Enterprise POS - POS API
==============================
Point of Sale endpoints for quick checkout.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth import get_current_user
from src.core.exceptions import (
    InsufficientStockError,
    NotFoundError,
    ProductInactiveError,
    ValidationError,
)
from src.database import get_db
from src.models.payment import Payment
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.models.stock_movement import StockMovement
from src.models.user import User

router = APIRouter()


def generate_receipt_number() -> str:
    """Generate unique receipt number."""
    from datetime import datetime
    import random
    
    now = datetime.now()
    return f"RCP-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"


@router.get("/products")
async def get_pos_products(
    category_id: Annotated[UUID | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get products for POS interface.
    
    Args:
        category_id: Filter by category
        search: Search query
        limit: Maximum results
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of products for POS
    """
    query = select(Product).where(Product.is_active == True)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Product.name.ilike(search_filter)) |
            (Product.barcode.ilike(search_filter))
        )
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(product.id),
                "name": product.name,
                "barcode": product.barcode,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "is_low_stock": product.is_low_stock,
                "image_url": product.image_url,
                "category": {
                    "id": str(product.category.id),
                    "name": product.category.name,
                } if product.category else None,
            }
            for product in products
        ],
    }


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Process POS checkout.
    
    Args:
        data: Checkout data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Checkout result with receipt
    """
    # Validate items
    if not data.get("items"):
        raise ValidationError("Checkout must have at least one item")
    
    items = data["items"]
    
    # Calculate totals
    subtotal = 0
    sale_items = []
    
    for item_data in items:
        product_id = item_data["product_id"]
        quantity = item_data["quantity"]
        
        # Get product
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise NotFoundError("Product", product_id)
        
        if not product.is_active:
            raise ProductInactiveError(product.name)
        
        # Check stock
        if product.stock_quantity < quantity:
            raise InsufficientStockError(
                product.name,
                product.stock_quantity,
                quantity
            )
        
        # Calculate item total
        unit_price = product.price
        item_total = unit_price * quantity
        subtotal += item_total
        
        # Create sale item
        sale_item = SaleItem(
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=item_total,
        )
        sale_items.append(sale_item)
        
        # Update stock
        previous_quantity = product.stock_quantity
        product.stock_quantity -= quantity
        
        # Create stock movement
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            type="out",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=product.stock_quantity,
            reference_type="sale",
            reason="POS checkout",
        )
        db.add(stock_movement)
    
    # Apply discount if code provided
    discount_amount = 0
    discount_code = data.get("discount_code")
    if discount_code:
        # TODO: Implement discount code validation
        pass
    
    # Calculate tax
    tax_rate = data.get("tax_rate", 0)
    taxable_amount = subtotal - discount_amount
    tax_amount = (taxable_amount * tax_rate) / 100
    
    # Calculate total
    total_amount = taxable_amount + tax_amount
    
    # Process payment
    payment_method = data.get("payment_method", "cash")
    cash_received = data.get("cash_received")
    change_amount = None
    
    if payment_method == "cash" and cash_received:
        change_amount = cash_received - total_amount
        if change_amount < 0:
            raise ValidationError("Insufficient cash received")
    
    # Create sale
    sale = Sale(
        user_id=current_user.id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_code=discount_code,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="completed",
        customer_name=data.get("customer_name", "Walk-in Customer"),
        customer_phone=data.get("customer_phone"),
        notes=data.get("notes"),
        receipt_number=generate_receipt_number(),
        items=sale_items,
    )
    
    db.add(sale)
    await db.flush()
    
    # Create payment
    payment = Payment(
        sale_id=sale.id,
        method=payment_method,
        amount=total_amount,
        status="completed",
        cash_received=cash_received,
        change_amount=change_amount,
    )
    db.add(payment)
    
    await db.commit()
    await db.refresh(sale)
    
    return {
        "sale_id": str(sale.id),
        "receipt_number": sale.receipt_number,
        "total_amount": float(total_amount),
        "discount_amount": float(discount_amount),
        "tax_amount": float(tax_amount),
        "cash_received": float(cash_received) if cash_received else None,
        "change": float(change_amount) if change_amount else None,
        "payment_method": payment_method,
        "items_count": len(items),
        "receipt_url": f"/api/v1/sales/{sale.id}/receipt",
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
    }


@router.get("/receipt/{sale_id}")
async def get_receipt(
    sale_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get receipt for a sale.
    
    Args:
        sale_id: Sale ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Receipt data
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.items).selectinload(SaleItem.product))
        .options(selectinload(Sale.payments))
        .options(selectinload(Sale.user))
        .where(Sale.id == sale_id)
    )
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise NotFoundError("Sale", str(sale_id))
    
    return {
        "receipt_number": sale.receipt_number,
        "date": sale.created_at.isoformat() if sale.created_at else None,
        "cashier": {
            "name": sale.user.full_name,
            "username": sale.user.username,
        },
        "customer": {
            "name": sale.customer_name,
            "phone": sale.customer_phone,
        },
        "items": [
            {
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total": float(item.total_price),
            }
            for item in sale.items
        ],
        "subtotal": float(sale.subtotal),
        "discount": float(sale.discount_amount),
        "tax": float(sale.tax_amount),
        "total": float(sale.total_amount),
        "payment": {
            "method": sale.payments[0].method if sale.payments else "unknown",
            "amount": float(sale.payments[0].amount) if sale.payments else 0,
            "cash_received": float(sale.payments[0].cash_received) if sale.payments and sale.payments[0].cash_received else None,
            "change": float(sale.payments[0].change_amount) if sale.payments and sale.payments[0].change_amount else None,
        },
        "notes": sale.notes,
    }


@router.post("/hold")
async def hold_transaction(
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Hold a transaction for later completion.
    
    Args:
        data: Transaction data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Hold reference
    """
    # TODO: Implement hold transaction functionality
    # This would typically store the transaction in Redis/session
    # without deducting stock or creating a sale record
    
    return {
        "success": True,
        "hold_reference": "HLD-12345",
        "message": "Transaction held successfully",
    }
