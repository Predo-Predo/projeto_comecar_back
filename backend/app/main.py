# backend/app/main.py

import os
import time
import requests
from typing import List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, SessionLocal
from .utils import prepare_project

# Cria as tabelas no banco caso ainda não existam
models.Base.metadata.create_all(bind=engine)

# Carrega variáveis de ambiente para GitHub
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN")
REPO_OWNER    = os.getenv("REPO_OWNER",   "Predo-Predo")
REPO_NAME     = os.getenv("REPO_NAME",    "projeto_comecar_back")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE","build.yml")

app = FastAPI(title="API de Empresas/Apps/Builds")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── Rotas de Empresa ────────────────────────────────────

@app.post("/empresas/", response_model=schemas.Empresa, status_code=201)
def criar_empresa(dados: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    if db.query(models.Empresa).filter(models.Empresa.cnpj == dados.cnpj).first():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    empresa = models.Empresa(**dados.dict())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@app.get("/empresas/", response_model=List[schemas.Empresa])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(models.Empresa).all()

# ─── Rotas de App ────────────────────────────────────────

@app.get("/apps/", response_model=List[schemas.App])
def listar_apps(db: Session = Depends(get_db)):
    return db.query(models.App).all()

# ─── Endpoint Único: Criar App + Build ───────────────────

@app.post(
    "/companies/{company_id}/build",
    response_model=schemas.Build,
    status_code=201,
    summary="Cria um App, registra um Build e dispara o workflow no GitHub"
)
def criar_app_e_disparar_build(
    company_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 1) Verifica se a empresa existe
    empresa = db.query(models.Empresa).get(company_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # 2) Cria um novo App no banco
    app_obj = models.App(company_id=company_id)
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)

    # 3) Registra o Build em “pending”
    build = models.Build(company_id=company_id, status="pending")
    db.add(build)
    db.commit()
    db.refresh(build)

    # 4) Prepara a cópia do template (gera slug e substitui placeholders)
    slug = prepare_project(company_name=empresa.name, bundle_id=empresa.bundle_id)

    # 5) Agenda o disparo do GitHub Actions em background
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

# ─── Função de background para disparar o GitHub Actions ──

def trigger_github_workflow(build_id: int):
    db = SessionLocal()
    try:
        build = db.query(models.Build).get(build_id)
        build.status = "in_progress"
        db.commit()

        # Cabeçalhos comuns
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept":        "application/vnd.github.v3+json"
        }

        # (Opcional) listar workflows disponíveis para debug
        workflows_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows"
        resp_wf = requests.get(workflows_url, headers=headers)
        print("[workflows] status_code=", resp_wf.status_code)
        print("[workflows] body=", resp_wf.json())

        # Dispara o workflow_dispatch convertendo company_id para string
        dispatch_url = (
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/actions/workflows/{WORKFLOW_FILE}/dispatches"
        )
        payload = {
            "ref": "main",
            "inputs": {
                "company_id": str(build.company_id)
            }
        }
        r = requests.post(dispatch_url, json=payload, headers=headers)
        print("[dispatch] status_code=", r.status_code, " text=", r.text)
        r.raise_for_status()  # deverá retornar 204

        # (Opcional) polling para buscar o run_id e acompanhar conclusão
        time.sleep(5)
        runs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
        r2 = requests.get(runs_url, headers=headers)
        runs = r2.json().get("workflow_runs", [])
        run = next((x for x in runs if x["head_branch"] == "main"), None)
        if run:
            build.workflow_run_id = str(run["id"])
            db.commit()

            status = run["status"]
            conclusion = run.get("conclusion")
            while status in ("queued", "in_progress"):
                time.sleep(5)
                rr = requests.get(f"{runs_url}/{build.workflow_run_id}", headers=headers)
                jr = rr.json()
                status     = jr["status"]
                conclusion = jr.get("conclusion")
            build.status = "success" if conclusion == "success" else "failure"
        else:
            build.status = "failure"
        db.commit()
    except Exception as e:
        print("[trigger_error]", repr(e))
        build = db.query(models.Build).get(build_id)
        build.status = "failure"
        db.commit()
    finally:
        db.close()
