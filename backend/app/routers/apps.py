# backend/app/routers/apps.py

import os
import shutil
from uuid import uuid4

import requests
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from slugify import slugify
from git import Repo

from .. import models, schemas, database
from ..utils import ensure_empresa_folder, clone_template_repo, _on_rm_error
from ..background import publicar_app_na_playstore  # nova função que criamos

router = APIRouter(prefix="/apps", tags=["apps"])

@router.post(
    "/",
    response_model=schemas.App,
    status_code=status.HTTP_201_CREATED
)
async def criar_app(
    background_tasks: BackgroundTasks,
    empresa_id: int = Form(...),
    projeto_id: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    logo_app: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db),
):
    # Verifica empresa
    result_empresa = await db.execute(select(models.Empresa).where(models.Empresa.id == empresa_id))
    empresa = result_empresa.scalars().first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # Verifica projeto
    result_projeto = await db.execute(select(models.Projeto).where(models.Projeto.id == projeto_id))
    projeto = result_projeto.scalars().first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # Slug do pacote
    slug_base = slugify(f"{empresa.nome}-{nome}")
    package_name = f"com.suaempresa.{slug_base}"

    # Salva logo
    logos_dir = os.path.join(os.getcwd(), "apps_logos")
    os.makedirs(logos_dir, exist_ok=True)
    logo_filename = f"{uuid4().hex}_{logo_app.filename}"
    logo_path = os.path.join(logos_dir, logo_filename)
    with open(logo_path, "wb") as out:
        out.write(await logo_app.read())

    # Cria registro no banco
    novo_app = models.App(
        empresa_id=empresa_id,
        projeto_id=projeto_id,
        nome=nome,
        descricao=descricao,
        logo_app=logo_path,
        package_name=package_name,
        esta_ativo=True
    )
    db.add(novo_app)
    await db.commit()
    await db.refresh(novo_app)

    # ✅ Tarefa em segundo plano
    background_tasks.add_task(publicar_app_na_playstore, novo_app.id)

    return novo_app
