import os
import shutil
from uuid import uuid4

import requests
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from slugify import slugify
from git import Repo

from .. import models, schemas, database
from ..utils import ensure_empresa_folder, clone_template_repo, _on_rm_error

router = APIRouter(prefix="/apps", tags=["apps"])

# Config GitHub
GITHUB_OWNER   = "Predo-Predo"
GITHUB_REPO    = "projeto_comecar_back"
WORKFLOW_FILE  = "android-release.yml"
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN")


@router.post(
    "/",
    response_model=schemas.App,
    status_code=status.HTTP_201_CREATED
)
async def criar_app(
    empresa_id: int = Form(...),
    projeto_id: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    logo_app: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    # 1) Verifica se a empresa existe
    empresa = db.query(models.Empresa).get(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # 2) Verifica se o projeto existe
    projeto = db.query(models.Projeto).get(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # 3) Gera o nome do package_name com slug
    slug_base = slugify(f"{empresa.nome}-{nome}")
    package_name = f"com.suaempresa.{slug_base}"

    # 4) Salva o arquivo de logo em disco
    logos_dir = os.path.join(os.getcwd(), "apps_logos")
    os.makedirs(logos_dir, exist_ok=True)
    logo_filename = f"{uuid4().hex}_{logo_app.filename}"
    logo_path = os.path.join(logos_dir, logo_filename)
    with open(logo_path, "wb") as out:
        out.write(await logo_app.read())

    # 5) Cria o App no banco
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
    db.commit()
    db.refresh(novo_app)

    # 6) Clona o repositório do template
    base_empresas_dir = os.path.join(os.getcwd(), "empresas")
    pasta_empresa = ensure_empresa_folder(base_empresas_dir, empresa.id, empresa.nome)
    projeto_slug = slugify(projeto.nome)
    project_clone_path = os.path.join(pasta_empresa, projeto_slug)

    try:
        clone_template_repo(projeto.repo_url, project_clone_path)
    except RuntimeError as e:
        db.delete(novo_app)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    # 7) Copia o JSON fixo de credenciais do Play Store
    android_dir = os.path.join(project_clone_path, "android")
    if not os.path.isdir(android_dir):
        shutil.rmtree(project_clone_path, onerror=_on_rm_error)
        db.delete(novo_app)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="Template Flutter não contém pasta 'android/'"
        )

    cred_path = os.path.abspath(os.path.join(os.getcwd(), "..", "credentials", "play-service-account.json"))
    try:
        with open(cred_path, "r", encoding="utf-8") as f:
            play_json = f.read()
    except FileNotFoundError:
        shutil.rmtree(project_clone_path, onerror=_on_rm_error)
        db.delete(novo_app)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="Credenciais do Google Play não encontradas em credentials/play-service-account.json"
        )

    with open(os.path.join(android_dir, "play-service-account.json"), "w", encoding="utf-8") as f:
        f.write(play_json)

    # 8) Commit e push
    try:
        repo = Repo(project_clone_path)
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "GitHub Action Bot")
            cw.set_value("user", "email", "action-bot@example.com")

        repo.git.add("android/play-service-account.json")
        repo.git.add(all=True)
        repo.index.commit(f"Configurar App {novo_app.id} para empresa {empresa.id}")
        repo.remote(name="origin").push(refspec="HEAD:main")
    except Exception as e:
        shutil.rmtree(project_clone_path, onerror=_on_rm_error)
        db.delete(novo_app)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erro no Git push: {e}")

    # 9) Dispara o GitHub Actions
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="Variável GITHUB_TOKEN não definida.")

    dispatch_url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/actions/workflows/{WORKFLOW_FILE}/dispatches"
    )
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    payload = {
        "ref": "main",
        "inputs": {"company_id": str(empresa.id)}
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
