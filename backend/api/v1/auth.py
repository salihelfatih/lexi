"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import TokenResponse, UserCreate, UserResponse
from backend.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_custom_auth_enabled_dependency,
    verify_password,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_custom_auth_enabled_dependency)],
)
async def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email.lower(), hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.id, email=user.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(require_custom_auth_enabled_dependency)],
)
async def login(request: Request, db: Session = Depends(get_db)):
    """Authenticate user and issue JWT."""
    form_data = await request.form()
    username = str(form_data.get("username", "")).lower()
    password = str(form_data.get("password", ""))

    user = db.query(User).filter(User.email == username, User.is_active.is_(True)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(id=current_user.id, email=current_user.email)
