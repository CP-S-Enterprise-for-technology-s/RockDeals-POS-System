"""
CP'S Enterprise POS - Reports API
==================================
Reporting and analytics endpoints.
"""

from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth import get_current_user
from src.database import get_db
from src.models.payment import Payment
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.models.user import User

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    period: Annotated[str, Query(pattern="^(today|yesterday|week|month|year)$")] = "today",
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard data.
    
    Args:
        period: Time period for data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dashboard data
    """
    # Calculate date range
    now = datetime.now()
    
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == "month":
        start_date = now - timedelta(days=30)
        end_date = now
    elif period == "year":
        start_date = now - timedelta(days=365)
        end_date = now
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    # Get sales data
    sales_query = (
        select(
            func.count(Sale.id).label("total_orders"),
            func.sum(Sale.total_amount).label("total_sales"),
            func.avg(Sale.total_amount).label("average_order_value"),
        )
        .where(Sale.created_at >= start_date)
        .where(Sale.created_at <= end_date)
        .where(Sale.status == "completed")
    )
    
    sales_result = await db.execute(sales_query)
    sales_data = sales_result.one()
    
    # Get products data
    products_query = select(func.count(Product.id)).where(Product.is_active == True)
    products_result = await db.execute(products_query)
    total_products = products_result.scalar()
    
    # Get low stock products
    low_stock_query = (
        select(func.count(Product.id))
        .where(Product.stock_quantity <= Product.min_stock_level)
        .where(Product.is_active == True)
    )
    low_stock_result = await db.execute(low_stock_query)
    low_stock_count = low_stock_result.scalar()
    
    # Get top selling products
    top_products_query = (
        select(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label("sold_quantity"),
            func.sum(SaleItem.total_price).label("revenue"),
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(Sale.created_at >= start_date)
        .where(Sale.created_at <= end_date)
        .where(Sale.status == "completed")
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(5)
    )
    
    top_products_result = await db.execute(top_products_query)
    top_products = top_products_result.all()
    
    # Get payment methods breakdown
    payment_query = (
        select(
            Payment.method,
            func.sum(Payment.amount).label("total"),
        )
        .join(Sale, Sale.id == Payment.sale_id)
        .where(Sale.created_at >= start_date)
        .where(Sale.created_at <= end_date)
        .where(Payment.status == "completed")
        .group_by(Payment.method)
    )
    
    payment_result = await db.execute(payment_query)
    payment_methods = {row.method: float(row.total) for row in payment_result.all()}
    
    # Calculate change percentage (compare with previous period)
    previous_start = start_date - (end_date - start_date)
    previous_sales_query = (
        select(func.sum(Sale.total_amount))
        .where(Sale.created_at >= previous_start)
        .where(Sale.created_at < start_date)
        .where(Sale.status == "completed")
    )
    
    previous_sales_result = await db.execute(previous_sales_query)
    previous_sales = previous_sales_result.scalar() or 0
    
    current_sales = sales_data.total_sales or 0
    if previous_sales > 0:
        change_percentage = ((current_sales - previous_sales) / previous_sales) * 100
    else:
        change_percentage = 0 if current_sales == 0 else 100
    
    return {
        "sales": {
            "total_sales": float(current_sales),
            "total_orders": sales_data.total_orders or 0,
            "average_order_value": float(sales_data.average_order_value or 0),
            "change_percentage": round(change_percentage, 2),
        },
        "products": {
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "top_selling": [
                {
                    "id": str(product.id),
                    "name": product.name,
                    "sold_quantity": int(product.sold_quantity),
                    "revenue": float(product.revenue),
                }
                for product in top_products
            ],
        },
        "payment_methods": payment_methods,
        "period": {
            "type": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    }


@router.get("/sales")
async def get_sales_report(
    start_date: Annotated[str, Query()] = None,
    end_date: Annotated[str, Query()] = None,
    group_by: Annotated[str, Query(pattern="^(day|week|month)$")] = "day",
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed sales report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        group_by: Grouping period
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Sales report data
    """
    # Parse dates
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()
    
    # Get summary
    summary_query = (
        select(
            func.count(Sale.id).label("total_orders"),
            func.sum(Sale.subtotal).label("subtotal"),
            func.sum(Sale.discount_amount).label("total_discounts"),
            func.sum(Sale.tax_amount).label("total_tax"),
            func.sum(Sale.total_amount).label("total_sales"),
        )
        .where(Sale.created_at >= start)
        .where(Sale.created_at <= end)
        .where(Sale.status == "completed")
    )
    
    summary_result = await db.execute(summary_query)
    summary = summary_result.one()
    
    # Get daily breakdown
    if group_by == "day":
        date_format = "%Y-%m-%d"
    elif group_by == "week":
        date_format = "%Y-%W"
    else:  # month
        date_format = "%Y-%m"
    
    # This is a simplified version - in production you'd use database-specific date functions
    daily_query = (
        select(
            func.date_trunc(group_by, Sale.created_at).label("period"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.total_amount).label("sales"),
        )
        .where(Sale.created_at >= start)
        .where(Sale.created_at <= end)
        .where(Sale.status == "completed")
        .group_by(func.date_trunc(group_by, Sale.created_at))
        .order_by(func.date_trunc(group_by, Sale.created_at))
    )
    
    daily_result = await db.execute(daily_query)
    daily_breakdown = daily_result.all()
    
    # Get top products
    top_products_query = (
        select(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label("quantity"),
            func.sum(SaleItem.total_price).label("revenue"),
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(Sale.created_at >= start)
        .where(Sale.created_at <= end)
        .where(Sale.status == "completed")
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
    )
    
    top_products_result = await db.execute(top_products_query)
    top_products = top_products_result.all()
    
    # Get top cashiers
    top_cashiers_query = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            func.count(Sale.id).label("orders"),
            func.sum(Sale.total_amount).label("sales"),
        )
        .join(Sale, Sale.user_id == User.id)
        .where(Sale.created_at >= start)
        .where(Sale.created_at <= end)
        .where(Sale.status == "completed")
        .group_by(User.id, User.first_name, User.last_name)
        .order_by(func.sum(Sale.total_amount).desc())
        .limit(10)
    )
    
    top_cashiers_result = await db.execute(top_cashiers_query)
    top_cashiers = top_cashiers_result.all()
    
    return {
        "summary": {
            "total_orders": summary.total_orders or 0,
            "subtotal": float(summary.subtotal or 0),
            "total_discounts": float(summary.total_discounts or 0),
            "total_tax": float(summary.total_tax or 0),
            "total_sales": float(summary.total_sales or 0),
        },
        "daily_breakdown": [
            {
                "period": row.period.isoformat() if row.period else None,
                "orders": row.orders,
                "sales": float(row.sales or 0),
            }
            for row in daily_breakdown
        ],
        "top_products": [
            {
                "id": str(product.id),
                "name": product.name,
                "quantity": int(product.quantity),
                "revenue": float(product.revenue),
            }
            for product in top_products
        ],
        "top_cashiers": [
            {
                "id": str(cashier.id),
                "name": f"{cashier.first_name} {cashier.last_name}",
                "orders": int(cashier.orders),
                "sales": float(cashier.sales),
            }
            for cashier in top_cashiers
        ],
    }


@router.get("/inventory")
async def get_inventory_report(
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get inventory report.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Inventory report data
    """
    # Get total inventory value
    inventory_value_query = (
        select(
            func.sum(Product.price * Product.stock_quantity).label("retail_value"),
            func.sum(Product.cost * Product.stock_quantity).label("cost_value"),
        )
        .where(Product.is_active == True)
    )
    
    inventory_value_result = await db.execute(inventory_value_query)
    inventory_value = inventory_value_result.one()
    
    # Get low stock products
    low_stock_query = (
        select(Product)
        .where(Product.stock_quantity <= Product.min_stock_level)
        .where(Product.is_active == True)
        .order_by(Product.stock_quantity)
    )
    
    low_stock_result = await db.execute(low_stock_query)
    low_stock_products = low_stock_result.scalars().all()
    
    # Get category breakdown
    category_query = (
        select(
            Product.category_id,
            func.count(Product.id).label("product_count"),
            func.sum(Product.stock_quantity).label("total_quantity"),
            func.sum(Product.price * Product.stock_quantity).label("value"),
        )
        .where(Product.is_active == True)
        .group_by(Product.category_id)
    )
    
    category_result = await db.execute(category_query)
    category_breakdown = category_result.all()
    
    return {
        "summary": {
            "retail_value": float(inventory_value.retail_value or 0),
            "cost_value": float(inventory_value.cost_value or 0),
            "profit_potential": float(
                (inventory_value.retail_value or 0) - (inventory_value.cost_value or 0)
            ),
        },
        "low_stock_alerts": [
            {
                "id": str(product.id),
                "name": product.name,
                "current_stock": product.stock_quantity,
                "min_stock": product.min_stock_level,
            }
            for product in low_stock_products
        ],
        "category_breakdown": [
            {
                "category_id": str(row.category_id) if row.category_id else None,
                "product_count": row.product_count,
                "total_quantity": int(row.total_quantity),
                "value": float(row.value or 0),
            }
            for row in category_breakdown
        ],
    }
