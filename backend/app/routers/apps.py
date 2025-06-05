# backend/app/routers/apps.py

import os
import shutil
import requests
import subprocess
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from slugify import slugify
from git import Repo, GitCommandError

from .. import models, schemas, database

router = APIRouter(prefix="/apps", tags=["apps"])

# ***********************************************
# Ajuste estes valores de acordo com seu repo!
GITHUB_OWNER   = "SEU_GITHUB_USER_OU_ORG"      # ex.: "minha-org"
GITHUB_REPO    = "projeto_comecar_back"        # ex.: "projeto_comecar_back"
WORKFLOW_FILE  = "android-release.yml"         # ou "build.yml", conforme seu workflow
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN")  # defina como variável de ambiente
# ***********************************************

def ensure_empresa_folder(base_dir: str, empresa_id: int, empresa_nome: str) -> str:
    """Cria (se não existir) a pasta base de uma empresa em `base_dir`."""
    slug = slugify(empresa_nome)
    pasta_empresa = os.path.join(base_dir, f"{empresa_id}-{slug}")
    os.makedirs(pasta_empresa, exist_ok=True)
    return pasta_empresa

def clone_template_repo(repo_url: str, dest_path: str) -> None:
    """
    Clona o repositório Git de `repo_url` em `dest_path`.
    Se `dest_path` já existir, apaga tudo lá dentro antes de clonar.
    """
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    parent = os.path.dirname(dest_path)
    os.makedirs(parent, exist_ok=True)

    try:
        Repo.clone_from(repo_url, dest_path)
    except GitCommandError as e:
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path)
        raise RuntimeError(f"Erro ao clonar repo {repo_url}: {e}")

    return

@router.post(
    "/",
    response_model=schemas.App,
    status_code=status.HTTP_201_CREATED
)
def criar_app(
    app_data: schemas.AppCreate,
    db: Session = Depends(database.get_db),
):
    # 1) Verifica se a empresa existe
    empresa = db.query(models.Empresa).filter(models.Empresa.id == app_data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    # 2) Verifica se o projeto existe
    projeto = db.query(models.Projeto).filter(models.Projeto.id == app_data.projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado")

    # 3) Gera uma chave amigável (slug) para o App
    chave_gerada = slugify(f"{empresa.nome}_{empresa.id}")

    # 4) Cria o novo objeto App (sem build/zip)
    novo_app = models.App(
        empresa_id          = app_data.empresa_id,
        logo_app_url        = app_data.logo_app_url,
        app_key             = chave_gerada,
        bundle_id           = None,
        package_name        = None,
        google_service_json = app_data.google_service_json,
        apple_team_id       = app_data.apple_team_id,
        apple_key_id        = app_data.apple_key_id,
        apple_issuer_id     = app_data.apple_issuer_id,
        projeto_id          = app_data.projeto_id,
        esta_ativo          = True,
    )

    # 5) Persiste no banco e obtém ID
    db.add(novo_app)
    db.commit()
    db.refresh(novo_app)

    # 6) Define caminhos
    base_empresas_dir = os.path.join(os.getcwd(), "empresas")  
    # ex.: "/caminho/para/seu/projeto/backend/empresas/"
    pasta_empresa = ensure_empresa_folder(base_empresas_dir, empresa.id, empresa.nome)

    # 7) Clona o repositório template
    projeto_slug = slugify(projeto.nome)
    project_clone_path = os.path.join(pasta_empresa, projeto_slug)
    try:
        clone_template_repo(projeto.repo_url, project_clone_path)
    except RuntimeError as e:
        # Se não conseguir clonar, apaga App recém-criado e devolve erro
        db.delete(novo_app)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    # 8) Copia o JSON de credenciais do Google Play para dentro do clone
    #    Se a empresa tiver enviado play_service_account_json, vamos gravar em:
    #    <project_clone_path>/android/play-service-account.json
    if empresa.play_service_account_json:
        # Pasta-alvo dentro do template clonado
        android_dir = os.path.join(project_clone_path, "android")
        if not os.path.isdir(android_dir):
            # se o template Flutter não tiver subpasta "android/", abortamos
            # e removemos tanto o clone quanto o registro de App
            shutil.rmtree(project_clone_path, ignore_errors=True)
            db.delete(novo_app)
            db.commit()
            raise HTTPException(
                status_code=500,
                detail="Template Flutter não contém pasta 'android/'"
            )

        # Caminho final do arquivo
        caminho_play_json = os.path.join(android_dir, "play-service-account.json")
        with open(caminho_play_json, "w", encoding="utf-8") as f:
            f.write(empresa.play_service_account_json)

    # 9) Dá git add + commit + push para enviar o código (incluindo o JSON) ao repositório GitHub
    try:
        repo = Repo(project_clone_path)
        # configurações de usuário (caso não existam)
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "GitHub Action Bot")
            cw.set_value("user", "email", "action-bot@example.com")

        # 9.1) Se o JSON foi escrito, inclua no commit
        if empresa.play_service_account_json:
            repo.git.add("android/play-service-account.json")

        # 9.2) Sempre commitamos algo para disparar o workflow, mesmo que só o código original
        repo.git.add(all=True)
        repo.index.commit(f"Configurar App {novo_app.id} para empresa {empresa.id}")

        # 9.3) Faz push para a branch principal (exemplo: main). Ajuste se usar outra branch.
        origin = repo.remote(name="origin")
        origin.push(refspec="HEAD:main")
    except Exception as e:
        # caso dê falha no push, removemos App e clone e retornamos erro
        shutil.rmtree(project_clone_path, ignore_errors=True)
        db.delete(novo_app)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erro no Git push: {e}")

    # 10) Disparar o workflow do GitHub Actions (via API) para que ele execute:
    #     - flutter build appbundle  
    #     - ./gradlew publishReleaseBundle  
    # Observe que o workflow do GitHub (arquivo .yml) deve já estar configurado
    # e possuir o nome `WORKFLOW_FILE` (job que faz build+publish).
    if not GITHUB_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Variável de ambiente GITHUB_TOKEN não definida."
        )

    dispatch_url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"actions/workflows/{WORKFLOW_FILE}/dispatches"
    )

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    payload = {
        "ref": "main",                       # branch onde seu workflow está
        "inputs": {
            "company_id": str(empresa.id)    # sempre como string
        }
    }

    resp = requests.post(dispatch_url, json=payload, headers=headers)
    if resp.status_code not in (204, 201):
        detalhe = resp.json().get("message", resp.text)
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao disparar GitHub Actions: {resp.status_code} - {detalhe}"
        )

    return novo_app


@router.get(
    "/",
    response_model=list[schemas.App]
)
def listar_apps(db: Session = Depends(database.get_db)):
    return db.query(models.App).order_by(models.App.created_at.desc()).all()
