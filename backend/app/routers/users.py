# backend/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import models, schemas
from app.database import get_db
from app.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("", response_model=schemas.UserOut)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Verifica se já existe
    result = await db.execute(
        select(models.User).where(models.User.email == user_in.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado"
        )
    # Cria novo usuário
    user = models.User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        nome=user_in.nome
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
