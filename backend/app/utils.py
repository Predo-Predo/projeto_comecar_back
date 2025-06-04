# backend/app/utils.py

import os
import shutil
from git import Repo, GitCommandError
from slugify import slugify

def ensure_empresa_folder(base_dir: str, empresa_id: int, empresa_nome: str) -> str:
    """
    Cria (se ainda não existir) a pasta base de uma empresa em `base_dir`, usando
    o formato "{empresa_id}-{slugify(empresa_nome)}". Retorna o caminho completo.
    Exemplo:
      base_dir="/home/user/PROJETO/empresas"
      empresa_id=3
      empresa_nome="Agência Demo"
    → cria "/home/user/PROJETO/empresas/3-agencia-demo" e devolve essa string.
    """
    slug = slugify(empresa_nome)
    pasta_empresa = os.path.join(base_dir, f"{empresa_id}-{slug}")
    os.makedirs(pasta_empresa, exist_ok=True)
    return pasta_empresa

def clone_template_repo(repo_url: str, dest_path: str) -> None:
    """
    Clona o repositório Git de `repo_url` em `dest_path`.
    Se `dest_path` já existir, apaga tudo lá dentro antes de clonar.
    Lança RuntimeError se o clone falhar.
    """
    # Se já existir algo em dest_path, remove para começar “limpo”
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    # Garante que a pasta pai de dest_path exista
    parent = os.path.dirname(dest_path)
    os.makedirs(parent, exist_ok=True)

    try:
        Repo.clone_from(repo_url, dest_path)
    except GitCommandError as e:
        # Se falhar, limpa parcialmente e relança como RuntimeError
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path)
        raise RuntimeError(f"Erro ao clonar repo {repo_url}: {e}")
    # Se chegar aqui, o clone deu certo. Dest_path agora contém o código do repositório.
    return
