"""
CP'S Enterprise POS - Sales API
================================
Sales management endpoints.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth import get_current_user
from src.core.exceptions import (
    BusinessLogicError,
    NotFoundError,
    ProductInactiveError,
    SaleAlreadyRefundedError,
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


@router.get("/")
async def list_sales(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    start_date: Annotated[str | None, Query()] = None,
    end_date: Annotated[str | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    status: Annotated[str | None, Query(pattern="^(pending|completed|cancelled|refunded)$")] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List sales with pagination and filtering.
    
    Args:
        page: Page number
        per_page: Items per page
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        user_id: Filter by user
        status: Filter by status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of sales
    """
    from datetime import datetime
    
    query = select(Sale)
    
    # Apply filters
    if start_date:
        query = query.where(Sale.created_at >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.where(Sale.created_at <= datetime.fromisoformat(end_date))
    
    if user_id:
        query = query.where(Sale.user_id == user_id)
    
    if status:
        query = query.where(Sale.status == status)
    
    # Get total count
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    query = query.order_by(Sale.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    sales = result.scalars().all()
    
    return {
        "items": [sale.to_dict() for sale in sales],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sale(
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new sale.
    
    Args:
        data: Sale creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created sale
    """
    # Validate items
    if not data.get("items"):
        raise ValidationError("Sale must have at least one item")
    
    # Calculate totals
    subtotal = 0
    sale_items = []
    
    for item_data in data["items"]:
        # Get product
        result = await db.execute(
            select(Product).where(Product.id == item_data["product_id"])
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise NotFoundError("Product", item_data["product_id"])
        
        if not product.is_active:
            raise ProductInactiveError(product.name)
        
        # Check stock
        quantity = item_data["quantity"]
        if product.stock_quantity < quantity:
            from src.core.exceptions import InsufficientStockError
            raise InsufficientStockError(
                product.name,
                product.stock_quantity,
                quantity
            )
        
        # Calculate item total
        unit_price = item_data.get("unit_price", product.price)
        item_discount = item_data.get("discount_amount", 0)
        item_total = (unit_price * quantity) - item_discount
        
        subtotal += item_total
        
        # Create sale item
        sale_item = SaleItem(
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=item_discount,
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
            reason="Sale transaction",
        )
        db.add(stock_movement)
    
    # Calculate discount
    discount_amount = data.get("discount_amount", 0)
    
    # Calculate tax
    tax_rate = data.get("tax_rate", 0)
    taxable_amount = subtotal - discount_amount
    tax_amount = (taxable_amount * tax_rate) / 100
    
    # Calculate total
    total_amount = taxable_amount + tax_amount
    
    # Create sale
    sale = Sale(
        user_id=current_user.id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_code=data.get("discount_code"),
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="completed",
        customer_name=data.get("customer_name"),
        customer_phone=data.get("customer_phone"),
        customer_email=data.get("customer_email"),
        notes=data.get("notes"),
        receipt_number=generate_receipt_number(),
        items=sale_items,
    )
    
    db.add(sale)
    await db.flush()  # Get sale ID
    
    # Create payment
    payment_data = data.get("payment", {})
    payment = Payment(
        sale_id=sale.id,
        method=payment_data.get("method", "cash"),
        amount=payment_data.get("amount", total_amount),
        transaction_id=payment_data.get("transaction_id"),
        reference_number=payment_data.get("reference_number"),
        status="completed",
        cash_received=payment_data.get("cash_received"),
        change_amount=payment_data.get("change_amount"),
        card_last_four=payment_data.get("card_last_four"),
        card_brand=payment_data.get("card_brand"),
        notes=payment_data.get("notes"),
    )
    db.add(payment)
    
    await db.commit()
    await db.refresh(sale)
    
    return sale.to_dict()


@router.get("/{sale_id}")
async def get_sale(
    sale_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get sale by ID.
    
    Args:
        sale_id: Sale ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Sale data
    """
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise NotFoundError("Sale", str(sale_id))
    
    return sale.to_dict()


@router.post("/{sale_id}/refund")
async def refund_sale(
    sale_id: UUID,
    data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Refund a sale.
    
    Args:
        sale_id: Sale ID
        data: Refund data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Refund result
    """
    # Check permissions
    if not current_user.is_manager:
        raise ValidationError("Only managers can process refunds")
    
    # Get sale
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise NotFoundError("Sale", str(sale_id))
    
    if sale.is_refunded:
        raise SaleAlreadyRefundedError()
    
    # Process refund items
    refund_items = data.get("items", [])
    refund_amount = 0
    
    for refund_item in refund_items:
        item_id = refund_item["item_id"]
        quantity = refund_item["quantity"]
        reason = refund_item.get("reason", "")
        
        # Find sale item
        sale_item = None
        for item in sale.items:
            if str(item.id) == item_id:
                sale_item = item
                break
        
        if not sale_item:
            raise NotFoundError("Sale item", item_id)
        
        if quantity > sale_item.quantity:
            raise ValidationError(f"Cannot refund more than purchased quantity for item {item_id}")
        
        # Calculate refund amount for this item
        item_refund = (sale_item.unit_price * quantity) - (sale_item.discount_amount * quantity / sale_item.quantity)
        refund_amount += item_refund
        
        # Restore stock
        product = sale_item.product
        previous_quantity = product.stock_quantity
        product.stock_quantity += quantity
        
        # Create stock movement
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            type="in",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=product.stock_quantity,
            reference_type="refund",
            reference_id=str(sale_id),
            reason=f"Refund: {reason}",
        )
        db.add(stock_movement)
    
    # Update sale status
    sale.status = "refunded"
    
    # Create refund payment record
    refund_payment = Payment(
        sale_id=sale.id,
        method="refund",
        amount=refund_amount,
        status="completed",
        notes=data.get("notes"),
    )
    db.add(refund_payment)
    
    await db.commit()
    
    return {
        "success": True,
        "refund_amount": refund_amount,
        "status": "completed",
        "processed_at": sale.updated_at.isoformat() if sale.updated_at else None,
    }
