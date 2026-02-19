"""
CP'S Enterprise POS - Payment Model
====================================
Payment model for transaction payments.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.sale import Sale


class Payment(Base):
    """Payment model for sale transactions."""

    __tablename__ = "payments"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign key to sale
    sale_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id"),
        nullable=False,
    )

    # Payment details
    method: Mapped[str] = mapped_column(
        Enum(
            "cash",
            "card",
            "bank_transfer",
            "mobile_payment",
            "gift_card",
            "other",
            name="payment_methods",
        ),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Transaction info
    transaction_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    reference_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "processing",
            "completed",
            "failed",
            "refunded",
            name="payment_status",
        ),
        default="pending",
        nullable=False,
    )

    # For cash payments
    cash_received: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    change_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # For card payments
    card_last_four: Mapped[Optional[str]] = mapped_column(
        String(4),
        nullable=True,
    )
    card_brand: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    sale: Mapped["Sale"] = relationship(
        "Sale",
        back_populates="payments",
    )

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == "completed"

    def to_dict(self) -> dict:
        """Convert payment to dictionary."""
        return {
            "id": str(self.id),
            "method": self.method,
            "amount": float(self.amount),
            "transaction_id": self.transaction_id,
            "reference_number": self.reference_number,
            "status": self.status,
            "cash_received": float(self.cash_received) if self.cash_received else None,
            "change_amount": float(self.change_amount) if self.change_amount else None,
            "card_last_four": self.card_last_four,
            "card_brand": self.card_brand,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, method={self.method}, amount={self.amount})>"
