# backend/app/background.py

import os
import shutil
import requests
from git import Repo
from slugify import slugify

from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models
from .database import SessionLocal  # <- agora usando sessão síncrona
from .utils import ensure_empresa_folder, clone_template_repo, _on_rm_error

# GitHub config
GITHUB_OWNER = "Predo-Predo"
GITHUB_REPO = "projeto_exemplo"
WORKFLOW_FILE = "android-release.yml"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def publicar_app_na_playstore(app_id: int):
    db: Session = SessionLocal()
    try:
        app = db.execute(select(models.App).where(models.App.id == app_id)).scalars().first()

        if not app:
            print(f"[ERRO] App {app_id} não encontrado")
            return

        empresa = db.execute(select(models.Empresa).where(models.Empresa.id == app.empresa_id)).scalars().first()
        projeto = db.execute(select(models.Projeto).where(models.Projeto.id == app.projeto_id)).scalars().first()

        if not empresa or not projeto:
            print(f"[ERRO] Dados incompletos para publicar app {app_id}")
            return

        base_empresas_dir = os.path.join(os.getcwd(), "empresas")
        pasta_empresa = ensure_empresa_folder(base_empresas_dir, empresa.id, empresa.nome)
        projeto_slug = slugify(projeto.nome)
        project_clone_path = os.path.join(pasta_empresa, projeto_slug)

        try:
            clone_template_repo(projeto.repo_url, project_clone_path)
        except RuntimeError as e:
            db.delete(app)
            db.commit()
            print(f"[ERRO] Clonagem falhou: {e}")
            return

        android_dir = os.path.join(project_clone_path, "android")
        if not os.path.isdir(android_dir):
            shutil.rmtree(project_clone_path, onerror=_on_rm_error)
            db.delete(app)
            db.commit()
            print("[ERRO] Pasta 'android/' não encontrada no template")
            return

        cred_path = os.path.abspath(os.path.join(os.getcwd(), "..", "credentials", "play-service-account.json"))
        try:
            with open(cred_path, "r", encoding="utf-8") as f:
                play_json = f.read()
        except FileNotFoundError:
            shutil.rmtree(project_clone_path, onerror=_on_rm_error)
            db.delete(app)
            db.commit()
            print("[ERRO] JSON de credenciais do Play Store não encontrado")
            return

        with open(os.path.join(android_dir, "play-service-account.json"), "w", encoding="utf-8") as f:
            f.write(play_json)

        try:
            repo = Repo(project_clone_path)
            with repo.config_writer() as cw:
                cw.set_value("user", "name", "GitHub Action Bot")
                cw.set_value("user", "email", "action-bot@example.com")

            repo.git.add("android/play-service-account.json")
            repo.git.add(all=True)
            repo.index.commit(f"Configurar App {app.id} para empresa {empresa.id}")
            repo.remote(name="origin").push(refspec="HEAD:main")
        except Exception as e:
            shutil.rmtree(project_clone_path, onerror=_on_rm_error)
            db.delete(app)
            db.commit()
            print(f"[ERRO] Git push falhou: {e}")
            return

        if not GITHUB_TOKEN:
            print("[ERRO] GITHUB_TOKEN não definido")
            return

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
            print(f"[ERRO] GitHub Actions falhou: {resp.status_code} - {resp.text}")
            return

        print(f"[OK] App {app.id} publicado com sucesso na Play Store!")

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao publicar app {app_id}: {e}")
    finally:
        db.close()
