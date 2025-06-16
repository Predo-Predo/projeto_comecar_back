# backend/app/utils.py

import os
import shutil
import subprocess
import zipfile
import stat
from git import Repo, GitCommandError
from slugify import slugify

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.models import User
from app.database import get_db


# --- JWT Utils: proteção de rotas ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# --- Clonagem e build do APK com Flutter ---
def _on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
    except Exception:
        pass
    func(path)

def ensure_empresa_folder(base_dir: str, empresa_id: int, empresa_nome: str) -> str:
    slug = slugify(empresa_nome)
    pasta_empresa = os.path.join(base_dir, f"{empresa_id}-{slug}")
    os.makedirs(pasta_empresa, exist_ok=True)
    return pasta_empresa

def clone_template_repo(repo_url: str, dest_path: str) -> None:
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path, onerror=_on_rm_error)

    parent = os.path.dirname(dest_path)
    os.makedirs(parent, exist_ok=True)

    try:
        Repo.clone_from(repo_url, dest_path)
    except GitCommandError as e:
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path, onerror=_on_rm_error)
        raise RuntimeError(f"Erro ao clonar repo {repo_url}: {e}")
    return

def build_apk_and_zip_with_flutter(project_path: str) -> str:
    if shutil.which("flutter") is None:
        raise RuntimeError(
            "Comando 'flutter' não encontrado no PATH.\n"
            "Abra um terminal onde 'flutter --version' retorne algo e inicie o Uvicorn/FastAPI nesse mesmo terminal."
        )

    try:
        proc_pub = subprocess.run(
            ["flutter", "pub", "get"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Falha ao executar 'flutter pub get': comando não encontrado.\n"
            "Verifique se 'flutter' está no PATH e se você iniciou o servidor na mesma sessão."
        )

    if proc_pub.returncode != 0:
        raise RuntimeError(f"Erro em 'flutter pub get': {proc_pub.stderr}")

    try:
        proc_build = subprocess.run(
            ["flutter", "build", "apk", "--release"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Falha ao executar 'flutter build apk': comando não encontrado.\n"
            "Verifique se 'flutter' está no PATH e se você iniciou o servidor na mesma sessão."
        )

    if proc_build.returncode != 0:
        raise RuntimeError(f"Erro em 'flutter build apk': {proc_build.stderr}")

    apk_path = os.path.join(
        project_path,
        "build",
        "app",
        "outputs",
        "flutter-apk",
        "app-release.apk"
    )
    if not os.path.isfile(apk_path):
        raise FileNotFoundError(f"APK não encontrado em: {apk_path}")

    build_dir = os.path.join(project_path, "build")
    os.makedirs(build_dir, exist_ok=True)
    zip_filename = "app_bundle.zip"
    zip_full_path = os.path.join(build_dir, zip_filename)

    with zipfile.ZipFile(zip_full_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(apk_path, arcname=os.path.basename(apk_path))

    try:
        repo = Repo(project_path)
    except Exception as e:
        raise RuntimeError(f"Erro ao abrir repositório Git em '{project_path}': {e}")

    rel_zip_path = os.path.relpath(zip_full_path, project_path)
    try:
        repo.index.add([rel_zip_path])
        repo.index.commit("Adiciona APK zipado do App")
        repo.remote(name="origin").push()
    except Exception as e:
        raise RuntimeError(f"Falha ao commitar/push: {e}")

    return zip_full_path
