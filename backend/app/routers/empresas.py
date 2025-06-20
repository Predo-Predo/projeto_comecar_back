# backend/app/routers/empresas.py

import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, schemas, database
from ..dependencies import get_current_user  # <== função que extrai o user do token

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.post(
    "/",
    response_model=schemas.Empresa,
    status_code=status.HTTP_201_CREATED
)
async def create_empresa(
    nome: str = Form(...),
    cnpj: str = Form(...),
    email_contato: str = Form(...),
    telefone: str = Form(...),
    logo_empresa: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),  # <== pega o user logado
):
    print(f"[DEBUG] Logo recebida: {logo_empresa.filename} ({logo_empresa.content_type})")

    result = await db.execute(select(models.Empresa).where(models.Empresa.cnpj == cnpj))
    exists = result.scalars().first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa com este CNPJ já cadastrada"
        )

    # Salva o logo no disco
    logos_dir = os.path.join(os.getcwd(), "logos")
    os.makedirs(logos_dir, exist_ok=True)
    filename = f"{uuid4().hex}_{logo_empresa.filename}"
    full_path = os.path.join(logos_dir, filename)
    contents = await logo_empresa.read()
    with open(full_path, "wb") as f:
        f.write(contents)

    nova = models.Empresa(
        nome=nome,
        cnpj=cnpj,
        email_contato=email_contato,
        telefone=telefone,
        logo_empresa=full_path,
        user_id=current_user.id  # <== associa ao usuário autenticado
    )
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return nova


@router.get(
    "/",
    response_model=list[schemas.Empresa]
)
async def listar_empresas(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Empresa).order_by(models.Empresa.created_at.desc()))
    return result.scalars().all()
