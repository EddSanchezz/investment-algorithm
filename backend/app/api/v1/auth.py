"""
QuantVision - Auth Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_password_hash, verify_password, create_access_token
from ..models.user import UserCreate, UserLogin, UserUpdate, UserResponse, TokenResponse
from ..models.user import User as UserModel
from ..models.user import UserProgress

router = APIRouter(prefix="/auth", tags=["auth"])


def _level_from_xp(xp: int) -> str:
    if xp >= 15001:
        return "Master"
    if xp >= 5001:
        return "Veteran"
    if xp >= 1501:
        return "Trader"
    if xp >= 501:
        return "Analyst"
    if xp >= 101:
        return "Explorer"
    return "Beginner"


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(UserModel).where(UserModel.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya esta registrado",
        )

    user = UserModel(
        email=data.email,
        password_hash=get_password_hash(data.password),
        name=data.name,
        auth_provider="email",
    )
    db.add(user)

    progress = UserProgress(
        user_id=user.id,
        xp="0",
        level="Beginner",
        streak_days=0,
    )
    db.add(progress)

    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


async def get_current_user(
    credentials = Depends(__import__("fastapi", fromlist=[" Depends"]).Depends(
        __import__("fastapi.security", fromlist=["HTTPBearer"]).HTTPBearer()
    )),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException, status
    from ..core.security import decode_access_token

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.name is not None:
        current_user.name = data.name
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)