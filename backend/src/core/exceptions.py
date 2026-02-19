"""
CP'S Enterprise POS - Custom Exceptions
========================================
Custom exception classes for the application.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "ERROR",
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.extra = extra or {}
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(AppException):
    """Validation error exception."""

    def __init__(self, detail: str = "Validation error", extra: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code="VALIDATION_ERROR",
            extra=extra,
        )


class AuthenticationError(AppException):
    """Authentication error exception."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED",
        )


class AuthorizationError(AppException):
    """Authorization error exception."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="FORBIDDEN",
        )


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code="NOT_FOUND",
        )


class ConflictError(AppException):
    """Resource conflict exception."""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code="CONFLICT",
        )


class RateLimitError(AppException):
    """Rate limit exceeded exception."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            code="RATE_LIMIT_EXCEEDED",
        )


class BusinessLogicError(AppException):
    """Business logic error exception."""

    def __init__(
        self,
        detail: str = "Business logic error",
        code: str = "BUSINESS_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            code=code,
        )


# Specific business errors
class InsufficientStockError(BusinessLogicError):
    """Insufficient stock error."""

    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            detail=f"Insufficient stock for '{product_name}'. Available: {available}, Requested: {requested}",
            code="INSUFFICIENT_STOCK",
        )


class InvalidPaymentError(BusinessLogicError):
    """Invalid payment error."""

    def __init__(self, detail: str = "Invalid payment"):
        super().__init__(
            detail=detail,
            code="INVALID_PAYMENT",
        )


class ProductInactiveError(BusinessLogicError):
    """Product inactive error."""

    def __init__(self, product_name: str):
        super().__init__(
            detail=f"Product '{product_name}' is not active",
            code="PRODUCT_INACTIVE",
        )


class SaleAlreadyRefundedError(BusinessLogicError):
    """Sale already refunded error."""

    def __init__(self):
        super().__init__(
            detail="Sale has already been refunded",
            code="SALE_ALREADY_REFUNDED",
        )


class InvalidDiscountCodeError(BusinessLogicError):
    """Invalid discount code error."""

    def __init__(self, detail: str = "Invalid discount code"):
        super().__init__(
            detail=detail,
            code="INVALID_DISCOUNT_CODE",
        )


class PaymentFailedError(BusinessLogicError):
    """Payment failed error."""

    def __init__(self, detail: str = "Payment processing failed"):
        super().__init__(
            detail=detail,
            code="PAYMENT_FAILED",
        )


# Exception handlers mapping
EXCEPTION_HANDLERS = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    BusinessLogicError: status.HTTP_400_BAD_REQUEST,
}
