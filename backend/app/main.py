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

# Carrega variáveis de ambiente obrigatórias
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN")
REPO_OWNER    = os.getenv("REPO_OWNER")
REPO_NAME     = os.getenv("REPO_NAME")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE")

if not all([GITHUB_TOKEN, REPO_OWNER, REPO_NAME, WORKFLOW_FILE]):
    raise RuntimeError(
        "As variáveis GITHUB_TOKEN, REPO_OWNER, REPO_NAME e WORKFLOW_FILE "
        "precisam estar definidas no .env"
    )

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
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
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


# --- Função de background que dispara o workflow ---

def trigger_github_workflow(build_id: int):
    db = SessionLocal()
    try:
        build = db.query(models.Build).get(build_id)
        build.status = "in_progress"
        db.commit()

        # Dispara o workflow_dispatch no GitHub
        dispatch_url = (
            f"https://api.github.com/repos/"
            f"{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
        )
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        payload = {
            "ref": "main",
            "inputs": {"company_id": build.company_id}
        }
        resp = requests.post(dispatch_url, json=payload, headers=headers)
        if resp.status_code != 204:
            raise RuntimeError(f"GitHub API retornou {resp.status_code}: {resp.text}")

        # Polling para capturar o run_id e acompanhar status
        time.sleep(5)
        runs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
        resp = requests.get(runs_url, headers=headers)
        runs = resp.json().get("workflow_runs", [])
        run = next(
            (r for r in runs if r["head_branch"] == "main" and r["name"] == "Build Flutter App"),
            None
        )
        if not run:
            build.status = "failure"
            db.commit()
            return

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
        db.commit()

    except Exception as e:
        # marca como falha e loga
        build = db.query(models.Build).get(build_id)
        build.status = "failure"
        db.commit()
        print(f"[trigger_github_workflow] erro: {e!r}")
    finally:
        db.close()


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
    # 1) registra no banco
    build = models.Build(company_id=company_id)
    db.add(build)
    db.commit()
    db.refresh(build)

    # 2) prepara projeto: copia template e faz replace, criando empresas/{id}-{slug}/
    pasta = prepare_project(
        company_id=build.company_id,
        company_name=build.empresa.name,
        bundle_id=build.empresa.bundle_id
    )

    # 3) agenda disparo do GitHub Actions em background
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
