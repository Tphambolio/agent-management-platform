"""Authentication routes"""
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import os
import httpx

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
from app.user_credentials import credentials_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes needed for Gemini API access
SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/generative-language.retriever"
]


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


# ================ GOOGLE OAUTH ENDPOINTS ================

@router.get("/google")
async def google_oauth_start():
    """
    Initiate Google OAuth flow
    Redirects user to Google's OAuth consent screen
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID environment variable."
        )

    # Build authorization URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",  # Get refresh token
        "prompt": "consent"  # Force consent to get refresh token
    }

    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{GOOGLE_AUTH_URL}?{query_string}"

    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_oauth_callback(code: str, response: Response, db: Session = Depends(get_db)):
    """
    Handle OAuth callback from Google
    Exchange authorization code for tokens and create/update user
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )

    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )

            if token_response.status_code != 200:
                print(f"Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")

            tokens = token_response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 3600)

            # Get user info from Google
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")

            userinfo = userinfo_response.json()

        # Create or update user in database
        google_id = userinfo.get("id")
        email = userinfo.get("email")

        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()

        if not user:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                google_id=google_id,
                email=email,
                full_name=userinfo.get("name"),
                profile_picture=userinfo.get("picture"),
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
        else:
            # Update existing user
            user.email = email
            user.full_name = userinfo.get("name")
            user.profile_picture = userinfo.get("picture")

        # Encrypt and store tokens
        user.google_access_token_encrypted = credentials_manager.encrypt(access_token)
        if refresh_token:  # Only update if we got a new one
            user.google_refresh_token_encrypted = credentials_manager.encrypt(refresh_token)

        user.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        user.last_login = datetime.utcnow()

        db.commit()
        db.refresh(user)

        user_id = user.id

        # Set session cookie
        redirect_response = RedirectResponse(url=f"{FRONTEND_URL}/?auth=success")
        redirect_response.set_cookie(
            key="session_id",
            value=user_id,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return redirect_response

    except HTTPException:
        raise
    except Exception as e:
        print(f"OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url=f"{FRONTEND_URL}/?auth=error")


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing session cookie
    """
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}


@router.get("/token")
async def get_user_token(session_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """
    Get user's Google access token (for Gemini API)
    Automatically refreshes if expired

    This endpoint is used internally by the backend to get tokens for API calls
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == session_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid session")

    # Check if token is expired
    if user.token_expires_at and user.token_expires_at < datetime.utcnow():
        # Need to refresh token
        if not user.google_refresh_token_encrypted:
            raise HTTPException(
                status_code=401,
                detail="No refresh token available. Please re-authenticate."
            )

        refresh_token = credentials_manager.decrypt(user.google_refresh_token_encrypted)

        try:
            async with httpx.AsyncClient() as client:
                refresh_response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token"
                    }
                )

                if refresh_response.status_code != 200:
                    print(f"Token refresh failed: {refresh_response.text}")
                    raise HTTPException(status_code=401, detail="Failed to refresh token")

                tokens = refresh_response.json()
                new_access_token = tokens.get("access_token")
                expires_in = tokens.get("expires_in", 3600)

                # Update user's access token
                user.google_access_token_encrypted = credentials_manager.encrypt(new_access_token)
                user.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                db.commit()

                return {"access_token": new_access_token, "expires_in": expires_in}

        except HTTPException:
            raise
        except Exception as e:
            print(f"Token refresh error: {e}")
            raise HTTPException(status_code=401, detail="Failed to refresh token")

    # Token still valid
    access_token = credentials_manager.decrypt(user.google_access_token_encrypted)
    return {"access_token": access_token}


@router.get("/session")
async def get_session_user(session_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """
    Get current user from session cookie
    Used by frontend to check authentication status
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == session_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "profile_picture": user.profile_picture,
        "authenticated": True
    }
