# backend/app/routers/apps.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from slugify import slugify
from .. import models, schemas, database

router = APIRouter(prefix="/apps", tags=["apps"])


@router.post(
    "/",
    response_model=schemas.App,
    status_code=status.HTTP_201_CREATED
)
def criar_app(
    app_data: schemas.AppCreate,
    db: Session = Depends(database.get_db),
):
    # Verifica se a empresa existe
    empresa = db.query(models.Empresa).filter(models.Empresa.id == app_data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    # Verifica se o projeto existe
    projeto = db.query(models.Projeto).filter(models.Projeto.id == app_data.projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado")

    # Gera uma chave amigável (slug) para o App
    chave_gerada = slugify(f"{empresa.nome}_{empresa.id}")

    novo_app = models.App(
        empresa_id=app_data.empresa_id,
        logo_app_url=app_data.logo_app_url,               # usa o campo logo_app_url
        app_key=chave_gerada,
        bundle_id=None,
        package_name=None,
        google_service_json=app_data.google_service_json,
        apple_team_id=app_data.apple_team_id,
        apple_key_id=app_data.apple_key_id,
        apple_issuer_id=app_data.apple_issuer_id,
        projeto_id=app_data.projeto_id,
        esta_ativo=True,
    )

    db.add(novo_app)
    db.commit()
    db.refresh(novo_app)
    return novo_app


@router.get(
    "/",
    response_model=list[schemas.App]
)
def listar_apps(db: Session = Depends(database.get_db)):
    return db.query(models.App).order_by(models.App.created_at.desc()).all()
