"""
CP'S Enterprise POS - Product Model
====================================
Product model for inventory management.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.category import Category
    from src.models.sale import SaleItem
    from src.models.stock_movement import StockMovement


class Product(Base):
    """Product model for inventory."""

    __tablename__ = "products"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Product info
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    barcode: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )
    sku: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    min_stock_level: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    max_stock_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Category
    category_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin",
    )
    sale_items: Mapped[List["SaleItem"]] = relationship(
        "SaleItem",
        back_populates="product",
        lazy="selectin",
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        lazy="selectin",
    )

    @property
    def is_low_stock(self) -> bool:
        """Check if product is low on stock."""
        return self.stock_quantity <= self.min_stock_level

    @property
    def profit_margin(self) -> Optional[Decimal]:
        """Calculate profit margin."""
        if self.cost and self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return None

    @property
    def total_value(self) -> Decimal:
        """Calculate total inventory value."""
        return self.price * self.stock_quantity

    def to_dict(self, include_cost: bool = False) -> dict:
        """Convert product to dictionary."""
        data = {
            "id": str(self.id),
            "name": self.name,
            "barcode": self.barcode,
            "sku": self.sku,
            "description": self.description,
            "price": float(self.price),
            "stock_quantity": self.stock_quantity,
            "min_stock_level": self.min_stock_level,
            "max_stock_level": self.max_stock_level,
            "is_low_stock": self.is_low_stock,
            "category": self.category.to_dict() if self.category else None,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_cost:
            data["cost"] = float(self.cost) if self.cost else None
            data["profit_margin"] = float(self.profit_margin) if self.profit_margin else None

        return data

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, stock={self.stock_quantity})>"
