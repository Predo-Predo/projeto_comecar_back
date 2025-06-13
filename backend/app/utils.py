# backend/app/utils.py

import os
import shutil
import subprocess
import zipfile
import stat
from git import Repo, GitCommandError
from slugify import slugify


def _on_rm_error(func, path, exc_info):
    """
    Callback para shutil.rmtree que tenta remover atributos de somente leitura
    e depois reaplica a operação.
    """
    try:
        # Remove flag de somente‐leitura (Windows) e tenta executar novamente
        os.chmod(path, stat.S_IWRITE)
    except Exception:
        pass
    func(path)


def ensure_empresa_folder(base_dir: str, empresa_id: int, empresa_nome: str) -> str:
    """
    Cria (se ainda não existir) a pasta base de uma empresa em `base_dir`,
    no formato "{empresa_id}-{slugify(empresa_nome)}". Retorna o caminho completo.
    """
    slug = slugify(empresa_nome)
    pasta_empresa = os.path.join(base_dir, f"{empresa_id}-{slug}")
    os.makedirs(pasta_empresa, exist_ok=True)
    return pasta_empresa


def clone_template_repo(repo_url: str, dest_path: str) -> None:
    """
    Clona o repositório Git de `repo_url` em `dest_path`.
    Se `dest_path` já existir, apaga tudo lá dentro antes de clonar,
    mesmo que haja arquivos marcados como somente leitura.
    Lança RuntimeError se o clone falhar.
    """
    # Se já existir algo em dest_path, remove para começar “limpo” (tratando arquivos readonly)
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path, onerror=_on_rm_error)

    # Garante que a pasta pai de dest_path exista
    parent = os.path.dirname(dest_path)
    os.makedirs(parent, exist_ok=True)

    try:
        Repo.clone_from(repo_url, dest_path)
    except GitCommandError as e:
        # Se falhar, limpa parcialmente e relança como RuntimeError
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path, onerror=_on_rm_error)
        raise RuntimeError(f"Erro ao clonar repo {repo_url}: {e}")
    return


def build_apk_and_zip_with_flutter(project_path: str) -> str:
    """
    1) Verifica se o comando 'flutter' está disponível no PATH.
       Se não estiver, lança RuntimeError informando que o Flutter não foi encontrado.
    2) Executa 'flutter pub get' em project_path
    3) Executa 'flutter build apk --release' em project_path
    4) Localiza o APK gerado em 'build/app/outputs/flutter-apk/app-release.apk'
    5) Compacta esse APK em 'build/app_bundle.zip'
    6) Usa GitPython para:
       - git add do ZIP
       - git commit -m "Adiciona APK zipado do App"
       - git push origin (branch atual)
    Retorna o caminho absoluto do .zip criado.
    """

    # 1) Verifica se 'flutter' existe no PATH
    if shutil.which("flutter") is None:
        raise RuntimeError(
            "Comando 'flutter' não encontrado no PATH.\n"
            "Abra um terminal onde 'flutter --version' retorne algo e inicie o Uvicorn/FastAPI nesse mesmo terminal."
        )

    # 2) flutter pub get
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

    # 3) flutter build apk --release
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

    # 4) Localiza o APK gerado
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

    # 5) Cola-o num ZIP
    build_dir = os.path.join(project_path, "build")
    os.makedirs(build_dir, exist_ok=True)
    zip_filename = "app_bundle.zip"
    zip_full_path = os.path.join(build_dir, zip_filename)

    with zipfile.ZipFile(zip_full_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(apk_path, arcname=os.path.basename(apk_path))

    # 6) Commit + Push do ZIP para o mesmo repositório Git
    try:
        repo = Repo(project_path)
    except Exception as e:
        raise RuntimeError(f"Erro ao abrir repositório Git em '{project_path}': {e}")

    rel_zip_path = os.path.relpath(zip_full_path, project_path)
    try:
        repo.index.add([rel_zip_path])
    except Exception as e:
        raise RuntimeError(f"Falha ao dar 'git add' em '{rel_zip_path}': {e}")

    try:
        repo.index.commit("Adiciona APK zipado do App")
    except Exception as e:
        raise RuntimeError(f"Falha ao commitar '{rel_zip_path}': {e}")

    try:
        origin = repo.remote(name="origin")
        origin.push()
    except GitCommandError as e:
        raise RuntimeError(f"Falha ao dar 'git push': {e}")

    return zip_full_path
