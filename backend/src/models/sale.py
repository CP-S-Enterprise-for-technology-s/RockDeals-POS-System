"""
CP'S Enterprise POS - Sale Model
=================================
Sale and sale item models for transaction management.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.product import Product
    from src.models.user import User


class Sale(Base):
    """Sale transaction model."""

    __tablename__ = "sales"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # User who made the sale
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    # Financials
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    discount_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        Enum("pending", "completed", "cancelled", "refunded", name="sale_status"),
        default="pending",
        nullable=False,
    )

    # Customer info
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    customer_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    customer_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Receipt
    receipt_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sales",
        lazy="selectin",
    )
    items: Mapped[List["SaleItem"]] = relationship(
        "SaleItem",
        back_populates="sale",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="sale",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def item_count(self) -> int:
        """Get total number of items in sale."""
        return sum(item.quantity for item in self.items)

    @property
    def is_completed(self) -> bool:
        """Check if sale is completed."""
        return self.status == "completed"

    @property
    def is_refunded(self) -> bool:
        """Check if sale is refunded."""
        return self.status == "refunded"

    @property
    def total_paid(self) -> Decimal:
        """Get total amount paid."""
        return sum(payment.amount for payment in self.payments if payment.status == "completed")

    @property
    def balance_due(self) -> Decimal:
        """Get remaining balance."""
        return self.total_amount - self.total_paid

    def to_dict(self) -> dict:
        """Convert sale to dictionary."""
        return {
            "id": str(self.id),
            "receipt_number": self.receipt_number,
            "user": {
                "id": str(self.user.id),
                "username": self.user.username,
                "full_name": self.user.full_name,
            },
            "items": [item.to_dict() for item in self.items],
            "subtotal": float(self.subtotal),
            "discount_amount": float(self.discount_amount),
            "discount_code": self.discount_code,
            "tax_rate": float(self.tax_rate),
            "tax_amount": float(self.tax_amount),
            "total_amount": float(self.total_amount),
            "status": self.status,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            "notes": self.notes,
            "item_count": self.item_count,
            "total_paid": float(self.total_paid),
            "balance_due": float(self.balance_due),
            "payments": [payment.to_dict() for payment in self.payments],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, receipt={self.receipt_number}, total={self.total_amount})>"


class SaleItem(Base):
    """Sale item model (line items in a sale)."""

    __tablename__ = "sale_items"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign keys
    sale_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id"),
        nullable=False,
    )
    product_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )

    # Item details
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="sale_items",
        lazy="selectin",
    )

    def to_dict(self) -> dict:
        """Convert sale item to dictionary."""
        return {
            "id": str(self.id),
            "product": {
                "id": str(self.product.id),
                "name": self.product.name,
                "barcode": self.product.barcode,
            },
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "discount_amount": float(self.discount_amount),
            "total_price": float(self.total_price),
        }

    def __repr__(self) -> str:
        return f"<SaleItem(id={self.id}, product={self.product.name}, qty={self.quantity})>"
