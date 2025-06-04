# backend/app/routers/apps.py

import os
import time
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from slugify import slugify

from .. import models, schemas, database
from ..utils import ensure_empresa_folder, clone_template_repo

router = APIRouter(prefix="/apps", tags=["apps"])


@router.post(
    "/",
    response_model=schemas.App,
    status_code=status.HTTP_201_CREATED
)
def criar_app(
    app_data: schemas.AppCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
):
    # 1) Verifica se a empresa existe
    empresa = db.query(models.Empresa).filter(models.Empresa.id == app_data.empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # 2) Verifica se o projeto (template) existe
    projeto = db.query(models.Projeto).filter(models.Projeto.id == app_data.projeto_id).first()
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )

    # 3) Gera uma chave amigável (slug) para o App
    chave_gerada = slugify(f"{empresa.nome}_{empresa.id}")

    # Se já existe um App com esta mesma chave, acrescenta timestamp para manter unicidade
    ja_existe = db.query(models.App).filter(models.App.app_key == chave_gerada).first()
    if ja_existe:
        chave_gerada = f"{chave_gerada}-{int(time.time())}"

    # 4) Cria o objeto App e salva no banco
    novo_app = models.App(
        empresa_id           = app_data.empresa_id,
        logo_app_url         = app_data.logo_app_url,
        app_key              = chave_gerada,
        bundle_id            = None,
        package_name         = None,
        google_service_json  = app_data.google_service_json,
        apple_team_id        = app_data.apple_team_id,
        apple_key_id         = app_data.apple_key_id,
        apple_issuer_id      = app_data.apple_issuer_id,
        projeto_id           = app_data.projeto_id,
        esta_ativo           = True,
    )

    db.add(novo_app)
    db.commit()
    db.refresh(novo_app)

    # 5) Dispara o clone do template em background:
    #    – Descobre a raiz do projeto (subimos 3 pastas a partir deste arquivo)
    raiz_do_projeto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    #    – Pasta "empresas" fica na raiz do repositório
    pasta_empresas = os.path.join(raiz_do_projeto, "empresas")

    # 5.1) Garante que exista a pasta da empresa: "<empresa.id>-<slugify(empresa.nome)>"
    pasta_da_empresa = ensure_empresa_folder(
        pasta_empresas,
        empresa.id,
        empresa.nome
    )

    # 5.2) Dentro da pasta da empresa, criamos a subpasta para este App:
    pasta_destino_clone = os.path.join(pasta_da_empresa, chave_gerada)

    # 5.3) Agenda o clone em background (não bloqueia a resposta HTTP)
    background_tasks.add_task(
        clone_template_repo,
        projeto.repo_url,
        pasta_destino_clone
    )

    # 6) Retorna o App criado (HTTP 201) imediatamente
    return novo_app


@router.get(
    "/",
    response_model=list[schemas.App]
)
def listar_apps(db: Session = Depends(database.get_db)):
    return db.query(models.App).order_by(models.App.created_at.desc()).all()
