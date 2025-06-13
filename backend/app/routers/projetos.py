# backend/app/routers/projetos.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/projetos",
    tags=["projetos"]
)

@router.get("", response_model=List[schemas.Projeto])
async def list_projetos(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(models.Projeto))
        projetos = result.scalars().all()
        return projetos
    except Exception as e:
        # opcional: logar o erro para debug
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar projetos: {e}"
        )

@router.post("", response_model=schemas.Projeto, status_code=status.HTTP_201_CREATED)
async def create_projeto(projeto_in: schemas.ProjetoCreate, db: AsyncSession = Depends(get_db)):
    proj = models.Projeto(**projeto_in.dict())
    db.add(proj)
    await db.commit()
    await db.refresh(proj)
    return proj
