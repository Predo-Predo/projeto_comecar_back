# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.responses import RedirectResponse

from app import models, schemas
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    oauth,
)

router = APIRouter(tags=["auth"])


# ——— Signup (e-mail + senha) ———
@router.post("/auth/signup", response_model=schemas.UserOut)
async def signup(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.email == user_in.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado"
        )
    user = models.User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ——— Login convencional ———
@router.post("/auth/login", response_model=schemas.Token)
async def login(user_in: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.email == user_in.email)
    )
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}


# ——— Login via Google (OIDC) ———
@router.get("/auth/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get(
    "/auth/google/callback",
    response_model=schemas.Token,
    name="auth_google_callback"
)
async def auth_google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    result = await db.execute(
        select(models.User).where(
            models.User.oauth_provider == "google",
            models.User.oauth_sub == user_info["sub"]
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        user = models.User(
            email=user_info["email"],
            oauth_provider="google",
            oauth_sub=user_info["sub"]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token}


# ——— Login via Apple (OIDC) ———
@router.get("/auth/apple")
async def login_apple(request: Request):
    redirect_uri = request.url_for("auth_apple_callback")
    return await oauth.apple.authorize_redirect(request, redirect_uri)


@router.get(
    "/auth/apple/callback",
    response_model=schemas.Token,
    name="auth_apple_callback"
)
async def auth_apple_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = await oauth.apple.authorize_access_token(request)
    user_info = await oauth.apple.parse_id_token(request, token)

    result = await db.execute(
        select(models.User).where(
            models.User.oauth_provider == "apple",
            models.User.oauth_sub == user_info["sub"]
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        user = models.User(
            email=user_info.get("email"),
            oauth_provider="apple",
            oauth_sub=user_info["sub"]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token}
