import os
import time
import requests
from typing import List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from .utils import prepare_project

# Cria tabelas se não existirem
models.Base.metadata.create_all(bind=engine)

# Variáveis de ambiente para GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER   = os.getenv("REPO_OWNER", "seu-usuario-ou-org")
REPO_NAME    = os.getenv("REPO_NAME", "seu-repo-modelo")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "build.yml")

app = FastAPI(title="API de Empresas/Apps/Builds")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Rotas Empresa ---

@app.post("/empresas/", response_model=schemas.Empresa, status_code=201)
def criar_empresa(dados: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Empresa).filter(models.Empresa.cnpj == dados.cnpj).first()
    if existe:
        raise HTTPException(400, "CNPJ já cadastrado")
    empresa = models.Empresa(**dados.dict())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@app.get("/empresas/", response_model=List[schemas.Empresa])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(models.Empresa).all()

# --- Rotas App ---

@app.post("/apps/", response_model=schemas.App, status_code=201)
def criar_app(dados: schemas.AppCreate, db: Session = Depends(get_db)):
    app_obj = models.App(company_id=dados.company_id)
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@app.get("/apps/", response_model=List[schemas.App])
def listar_apps(db: Session = Depends(get_db)):
    return db.query(models.App).all()

# --- Rotas Build ---

@app.post(
    "/companies/{company_id}/build",
    response_model=schemas.Build,
    status_code=201
)
def disparar_build(
    company_id: int,
    build_in: schemas.BuildCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 1) registra
    build = models.Build(company_id=company_id)
    db.add(build)
    db.commit()
    db.refresh(build)

    # 2) prepara projeto (cópia e replace)
    slug = prepare_project(build.empresa.name, build.empresa.bundle_id)
    # opcional: git add/commit/push da pasta gerada
    # os.system(f"git add empresas/{slug} && git commit -m 'Add {slug}' && git push")

    # 3) agenda trigger GitHub Actions
    background_tasks.add_task(trigger_github_workflow, build.id)

    return build

@app.get(
    "/companies/{company_id}/builds",
    response_model=List[schemas.Build]
)
def listar_builds(company_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Build)
          .filter(models.Build.company_id == company_id)
          .order_by(models.Build.created_at.desc())
          .all()
    )

# --- Função de background ---

def trigger_github_workflow(build_id: int):
    db = SessionLocal()
    try:
        build = db.query(models.Build).get(build_id)
        build.status = "in_progress"
        db.commit()

        # dispatch workflow
        dispatch_url = (
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/actions/workflows/{WORKFLOW_FILE}/dispatches"
        )
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {"ref": "main", "inputs": {"company_id": build.company_id}}
        r = requests.post(dispatch_url, json=payload, headers=headers)
        r.raise_for_status()

        # polling do run_id e conclusão
        time.sleep(5)
        runs_url = (
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/actions/runs"
        )
        r = requests.get(runs_url, headers=headers)
        runs = r.json().get("workflow_runs", [])
        run = next((r for r in runs if r["head_branch"] == "main"), None)
        if run:
            build.workflow_run_id = str(run["id"])
            db.commit()

            status = run["status"]
            conclusion = run.get("conclusion")
            while status in ("in_progress", "queued"):
                time.sleep(5)
                rr = requests.get(f"{runs_url}/{build.workflow_run_id}", headers=headers)
                jr = rr.json()
                status = jr["status"]
                conclusion = jr.get("conclusion")
            build.status = "success" if conclusion == "success" else "failure"
        else:
            build.status = "failure"

        db.commit()
    finally:
        db.close()
