"""Authentication routes"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.validators.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.auth.jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id
)
from app.middleware.error_handler import (
    NotFoundException,
    ValidationException,
    AuthenticationException,
    DatabaseException
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user

    Creates a new user account with the provided credentials.
    Returns an access token upon successful registration.

    Raises:
        ValidationException: If username or email already exists
        DatabaseException: If database operation fails
    """
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise ValidationException("Username already exists")

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise ValidationException("Email already exists")

        # Create new user
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(request.password)

        new_user = User(
            id=user_id,
            username=request.username,
            email=request.email,
            hashed_password=hashed_pwd,
            full_name=request.full_name,
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create access token
        token_data = {
            "user_id": user_id,
            "username": request.username,
            "email": request.email
        }
        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            username=request.username
        )

    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(f"Failed to create user: {str(e)}") from e
    except Exception as e:
        db.rollback()
        raise


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user

    Authenticates a user with username and password.
    Returns an access token upon successful authentication.

    Raises:
        AuthenticationException: If credentials are invalid or user is inactive
        NotFoundException: If user doesn't exist
    """
    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise AuthenticationException("Invalid username or password")

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise AuthenticationException("Invalid username or password")

    # Check if user is active
    if not user.is_active:
        raise AuthenticationException("User account is inactive")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current user information

    Returns the profile information of the currently authenticated user.
    Requires a valid JWT token in the Authorization header.

    Raises:
        NotFoundException: If user doesn't exist
        AuthenticationException: If token is invalid
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise NotFoundException("User", user_id)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user by ID

    Returns the profile information of a specific user.
    Requires authentication.

    Raises:
        NotFoundException: If user doesn't exist
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise NotFoundException("User", user_id)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login
    )
