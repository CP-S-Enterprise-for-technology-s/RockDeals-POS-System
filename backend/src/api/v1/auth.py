"""
CP'S Enterprise POS - Authentication API
=========================================
Authentication endpoints for the API.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ValidationError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    verify_token_type,
)
from src.database import get_db
from src.models.user import User
from src.schemas.user import (
    PasswordChange,
    PasswordReset,
    PasswordResetRequest,
    TokenRefresh,
    TokenRefreshResponse,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserResponse,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        User: Current user
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    payload = decode_token(token)
    
    if not payload or not verify_token_type(token, "access"):
        raise AuthenticationError("Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is deactivated")
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


@router.post("/login", response_model=UserLoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Login with username and password.
    
    Args:
        form_data: Login form data
        db: Database session
        
    Returns:
        UserLoginResponse: Access and refresh tokens
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        raise AuthenticationError("Invalid username or password")
    
    if not user.is_active:
        raise AuthenticationError("User account is deactivated")
    
    # Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        data: Refresh token data
        db: Database session
        
    Returns:
        TokenRefreshResponse: New access and refresh tokens
    """
    # Verify refresh token
    if not verify_token_type(data.refresh_token, "refresh"):
        raise AuthenticationError("Invalid refresh token")
    
    payload = decode_token(data.refresh_token)
    if not payload:
        raise AuthenticationError("Invalid or expired refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    # Verify user exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    # Generate new tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenRefreshResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Logout current user.
    
    Note: In a stateless JWT system, logout is handled client-side
    by removing the tokens. For server-side token revocation,
    a token blacklist would be needed.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # TODO: Implement token blacklist for server-side logout
    return {"success": True, "message": "Logged out successfully"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user
        
    Raises:
        ConflictError: If username or email already exists
    """
    if not settings.enable_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled",
        )
    
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    if result.scalar_one_or_none():
        raise ValidationError("Username already exists")
    
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    if result.scalar_one_or_none():
        raise ValidationError("Email already exists")
    
    # Create user
    user = User(
        username=data.username,
        email=data.email,
        password_hash=data.password,  # Already hashed in schema
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        is_active=data.is_active,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/password/change")
async def change_password(
    data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user's password.
    
    Args:
        data: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        raise ValidationError("Current password is incorrect")
    
    # Update password
    from src.core.security import get_password_hash
    current_user.password_hash = get_password_hash(data.new_password)
    
    await db.commit()
    
    return {"success": True, "message": "Password changed successfully"}


@router.post("/password/reset-request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset.
    
    Args:
        data: Password reset request data
        db: Database session
        
    Returns:
        Success message (always return success to prevent email enumeration)
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # TODO: Send password reset email
        pass
    
    # Always return success to prevent email enumeration
    return {
        "success": True,
        "message": "If the email exists, a password reset link has been sent",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return UserResponse.model_validate(current_user)
