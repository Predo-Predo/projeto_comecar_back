# backend/app/utils.py

import os
import shutil
import subprocess
from zipfile import ZipFile

from git import Repo, GitCommandError
from slugify import slugify

def ensure_empresa_folder(base_dir: str, empresa_id: int, empresa_nome: str) -> str:
    """
    Cria (se ainda não existir) a pasta base de uma empresa em `base_dir`, usando
    o formato "{empresa_id}-{slugify(empresa_nome)}". Retorna o caminho completo.
    Exemplo:
      base_dir="/home/user/PROJETO_COMECAR_BACK/empresas"
      empresa_id=3
      empresa_nome="Agência Demo"
    → cria "/home/user/PROJETO_COMECAR_BACK/empresas/3-agencia-demo" e devolve essa string.
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
    # Se chegar aqui, o clone deu certo. dest_path agora contém o código do repositório.
    return

def build_and_zip_app(empresa_id: int, empresa_nome: str, app_key: str) -> str:
    """
    1) Monta o caminho da pasta do App em `empresas/{empresa_id}-{slug(empresa_nome)}/{app_key}`.
    2) Entra nessa pasta e executa 'flutter build apk --release'.
    3) Após gerar o APK (app-release.apk), cria um ZIP com todo esse diretório do App,
       nomeando-o como '{app_key}.zip', e salva em 'empresas/{empresa_id}-{slug(empresa_nome)}/'.
    4) Retorna o caminho absoluto do ZIP gerado.
    """

    # === 1) Descobre onde fica a raiz do projeto_comecar_back ===
    #
    # utils.py está em:   PROJETO_COMECAR_BACK/backend/app/utils.py
    # Para chegar em PROJETO_COMECAR_BACK, subimos duas pastas:
    #    1) de "backend/app"  para  "backend"
    #    2) de "backend"      para  "projeto_comecar_back"
    #
    raiz_do_projeto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    # Agora raiz_do_projeto == ".../projetos/projeto_comecar_back"

    # === 2) Monta as strings com slug e caminhos ===
    slug_empresa = slugify(empresa_nome)
    pasta_empresas = os.path.join(raiz_do_projeto, "empresas")
    pasta_da_empresa = os.path.join(pasta_empresas, f"{empresa_id}-{slug_empresa}")
    pasta_app = os.path.join(pasta_da_empresa, app_key)  # ex.: ".../empresas/3-agencia-digital-futuro/algum-app-key"

    # === 3) Verifica se existe a pasta do App ===
    if not os.path.isdir(pasta_app):
        raise RuntimeError(f"Pasta do App não encontrada: {pasta_app}")

    # === 4) Executa o Flutter build dentro da pasta do App ===
    #
    # Supondo que o Flutter esteja no PATH de sistema, rodamos:
    #    flutter build apk --release
    # dentro de pasta_app. Isso gera:
    #    pasta_app/build/app/outputs/apk/release/app-release.apk
    #
    cmd_build = ["flutter", "build", "apk", "--release", "--target-platform=android-arm64"]
    proc = subprocess.Popen(
        cmd_build,
        cwd=pasta_app,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # Exibe linha a linha para debug
    for linha in proc.stdout:
        print(linha, end="")

    exit_code = proc.wait()
    if exit_code != 0:
        raise RuntimeError(f"'flutter build apk' retornou código {exit_code}")

    # === 5) Encontra o APK gerado ===
    apk_relativo = "build/app/outputs/flutter-apk/app-release.apk"
    apk_gerado = os.path.join(pasta_app, apk_relativo)
    if not os.path.isfile(apk_gerado):
        raise RuntimeError(f"APK não encontrado em: {apk_gerado}")

    # === 6) Cria o arquivo ZIP na pasta da empresa ===
    zip_destino = os.path.join(pasta_da_empresa, f"{app_key}.zip")
    # Se já existir algum ZIP anterior, apaga:
    if os.path.isfile(zip_destino):
        os.remove(zip_destino)

    # Compacta toda a pasta do App dentro do ZIP
    with ZipFile(zip_destino, "w") as zipf:
        for root, _, arquivos in os.walk(pasta_app):
            for nome_arquivo in arquivos:
                caminho_absoluto = os.path.join(root, nome_arquivo)
                # Para “preservar” a estrutura interna, pegamos o caminho relativo a pasta_app:
                rel_path = os.path.relpath(caminho_absoluto, pasta_app)
                zipf.write(caminho_absoluto, arcname=os.path.join(app_key, rel_path))

    return zip_destino
