# backend/app/routers/apps.py

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from slugify import slugify

from .. import models, schemas, database, utils

router = APIRouter(prefix="/apps", tags=["apps"])


@router.post(
    "/",
    response_model=schemas.AppWithZip,
    status_code=status.HTTP_201_CREATED
)
def criar_app(
    app_data: schemas.AppCreate,
    db: Session = Depends(database.get_db),
):
    """
    1) Verifica se a empresa existe;
    2) Verifica se o projeto existe;
    3) Gera o app_key (slug);
    4) Cria a pasta base da empresa (se necessário);
    5) Clona o repositório do template dentro de empresas/<empresa_slug>/<app_key>;
    6) Insere o novo App no banco;
    7) Roda build_and_zip_app(...) para gerar o APK e o ZIP;
    8) Retorna todos os campos de App + campo 'zip_path'.
    """

    # ----------------------------------------------------------------
    # 1) Verifica se a empresa existe no banco
    empresa = (
        db.query(models.Empresa)
          .filter(models.Empresa.id == app_data.empresa_id)
          .first()
    )
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # ----------------------------------------------------------------
    # 2) Verifica se o projeto (template) existe no banco
    projeto = (
        db.query(models.Projeto)
          .filter(models.Projeto.id == app_data.projeto_id)
          .first()
    )
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )

    # ----------------------------------------------------------------
    # 3) Gera a chave amigável (slug) para o App
    chave_gerada = slugify(f"{empresa.nome}_{empresa.id}")

    # ----------------------------------------------------------------
    # 4) Cria (se não existir) a pasta base da empresa:
    #    - Base: <repositório-raiz>/empresas
    #    - Pasta da empresa: <empresa_id>-<slug(empresa.nome)>
    #    (por exemplo: "3-agencia-digital-futuro")
    base_empresas_dir = os.path.join(os.getcwd(), "empresas")
    pasta_empresa = utils.ensure_empresa_folder(
        base_dir=base_empresas_dir,
        empresa_id=empresa.id,
        empresa_nome=empresa.nome
    )

    # ----------------------------------------------------------------
    # 5) Clona o repositório do template Flutter dentro da subpasta <app_key>
    #    Exemplo de destino:
    #      <base_empresas_dir>/<empresa_slug>/<app_key>
    destino_clonagem = os.path.join(pasta_empresa, chave_gerada)
    try:
        utils.clone_template_repo(
            repo_url = projeto.repo_url,
            dest_path = destino_clonagem
        )
    except RuntimeError as clone_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao clonar o template: {clone_err}"
        )

    # ----------------------------------------------------------------
    # 6) Insere o novo App no banco
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

    # ----------------------------------------------------------------
    # 7) Roda o build + gera o ZIP
    #     build_and_zip_app inespera que o projeto Flutter válido esteja em:
    #       <pasta_empresa>/<app_key>
    try:
        zip_path = utils.build_and_zip_app(
            empresa.id,
            empresa.nome,
            novo_app.app_key
        )
    except RuntimeError as e:
        # Se o build falhar (por exemplo, Flutter não instalado, erros de dependências etc.),
        # limpamos ou ao menos informamos o problema.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao compilar/zipar o App: {e}"
        )

    # ----------------------------------------------------------------
    # 8) Retorna todos os campos de App + o campo extra 'zip_path'
    return {
        "empresa_id":           novo_app.empresa_id,
        "logo_app_url":         novo_app.logo_app_url,
        "google_service_json":  novo_app.google_service_json,
        "apple_team_id":        novo_app.apple_team_id,
        "apple_key_id":         novo_app.apple_key_id,
        "apple_issuer_id":      novo_app.apple_issuer_id,
        "projeto_id":           novo_app.projeto_id,
        "id":                   novo_app.id,
        "app_key":              novo_app.app_key,
        "bundle_id":            novo_app.bundle_id,
        "package_name":         novo_app.package_name,
        "esta_ativo":           novo_app.esta_ativo,
        "created_at":           novo_app.created_at,
        "zip_path":             zip_path,
    }


@router.get(
    "/",
    response_model=list[schemas.App]
)
def listar_apps(db: Session = Depends(database.get_db)):
    return db.query(models.App).order_by(models.App.created_at.desc()).all()
