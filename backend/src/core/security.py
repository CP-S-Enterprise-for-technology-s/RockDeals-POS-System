"""
CP'S Enterprise POS - Security Module
======================================
Authentication, authorization, and security utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: The plain text password
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional custom expiration time
        extra_claims: Optional additional claims to include
        
    Returns:
        The encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional custom expiration time
        
    Returns:
        The encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify that a token is of the expected type.
    
    Args:
        token: The JWT token
        expected_type: The expected token type (access or refresh)
        
    Returns:
        True if token type matches, False otherwise
    """
    payload = decode_token(token)
    if not payload:
        return False
    return payload.get("type") == expected_type


class PermissionChecker:
    """Permission checking utilities."""

    # Role hierarchy (higher roles have more permissions)
    ROLE_HIERARCHY = {
        "admin": 4,
        "manager": 3,
        "cashier": 2,
        "viewer": 1,
    }

    # Permission matrix
    PERMISSIONS = {
        "users": {
            "create": ["admin"],
            "read": ["admin", "manager", "cashier"],
            "update": ["admin", "manager"],
            "delete": ["admin"],
        },
        "products": {
            "create": ["admin", "manager"],
            "read": ["admin", "manager", "cashier", "viewer"],
            "update": ["admin", "manager"],
            "delete": ["admin"],
        },
        "sales": {
            "create": ["admin", "manager", "cashier"],
            "read": ["admin", "manager", "cashier"],
            "update": ["admin", "manager"],
            "delete": ["admin"],
        },
        "reports": {
            "read": ["admin", "manager"],
        },
        "settings": {
            "read": ["admin", "manager"],
            "update": ["admin"],
        },
    }

    @classmethod
    def has_permission(cls, user_role: str, resource: str, action: str) -> bool:
        """
        Check if a user role has permission for a specific action on a resource.
        
        Args:
            user_role: The user's role
            resource: The resource to check (e.g., 'products', 'sales')
            action: The action to check (e.g., 'create', 'read', 'update', 'delete')
            
        Returns:
            True if permission is granted, False otherwise
        """
        if user_role == "admin":
            return True  # Admin has all permissions

        resource_perms = cls.PERMISSIONS.get(resource, {})
        allowed_roles = resource_perms.get(action, [])

        return user_role in allowed_roles

    @classmethod
    def has_higher_or_equal_role(cls, user_role: str, required_role: str) -> bool:
        """
        Check if a user has a higher or equal role in the hierarchy.
        
        Args:
            user_role: The user's role
            required_role: The required minimum role
            
        Returns:
            True if user's role is higher or equal, False otherwise
        """
        user_level = cls.ROLE_HIERARCHY.get(user_role, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: The length of the token in bytes
        
    Returns:
        A secure random token as a hex string
    """
    import secrets
    return secrets.token_hex(length)


def sanitize_input(value: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        value: The input string to sanitize
        
    Returns:
        The sanitized string
    """
    import html
    return html.escape(value.strip())
