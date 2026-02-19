"""
CP'S Enterprise POS - Users API
================================
User management endpoints.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth import get_current_active_user, get_current_user
from src.core.exceptions import ConflictError, NotFoundError, ValidationError
from src.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query()] = None,
    role: Annotated[str | None, Query(pattern="^(admin|manager|cashier|viewer)$")] = None,
    is_active: Annotated[bool | None, Query()] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List users with pagination and filtering.
    
    Args:
        page: Page number
        per_page: Items per page
        search: Search query for username, email, or name
        role: Filter by role
        is_active: Filter by active status
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserListResponse: Paginated list of users
    """
    # Build query
    query = select(User)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (User.username.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.first_name.ilike(search_filter)) |
            (User.last_name.ilike(search_filter))
        )
    
    if role:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count
    count_result = await db.execute(select(User).where(query.whereclause))
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.
    
    Args:
        data: User creation data
        current_user: Current authenticated user (must be admin or manager)
        db: Database session
        
    Returns:
        UserResponse: Created user
    """
    # Check permissions
    if not current_user.is_manager:
        raise ValidationError("Only managers can create users")
    
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    if result.scalar_one_or_none():
        raise ConflictError(f"Username '{data.username}' already exists")
    
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    if result.scalar_one_or_none():
        raise ConflictError(f"Email '{data.email}' already exists")
    
    # Create user
    user = User(
        username=data.username,
        email=data.email,
        password_hash=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        is_active=data.is_active,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: User data
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", str(user_id))
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update user.
    
    Args:
        user_id: User ID
        data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    # Check permissions
    if str(current_user.id) != str(user_id) and not current_user.is_manager:
        raise ValidationError("You can only update your own profile")
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", str(user_id))
    
    # Check if trying to change role (only admins can do this)
    if data.role and data.role != user.role and not current_user.is_admin:
        raise ValidationError("Only admins can change user roles")
    
    # Check if username is being changed and if it already exists
    if data.username and data.username != user.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"Username '{data.username}' already exists")
        user.username = data.username
    
    # Check if email is being changed and if it already exists
    if data.email and data.email != user.email:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise ConflictError(f"Email '{data.email}' already exists")
        user.email = data.email
    
    # Update fields
    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.role:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = data.password
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user (soft delete).
    
    Args:
        user_id: User ID
        current_user: Current authenticated user (must be admin)
        db: Database session
        
    Returns:
        Success message
    """
    # Check permissions
    if not current_user.is_admin:
        raise ValidationError("Only admins can delete users")
    
    # Prevent self-deletion
    if str(current_user.id) == str(user_id):
        raise ValidationError("You cannot delete your own account")
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", str(user_id))
    
    # Soft delete
    user.is_active = False
    await db.commit()
    
    return {"success": True, "message": "User deleted successfully"}
