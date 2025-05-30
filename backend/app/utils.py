import os
import shutil
from pathlib import Path
from slugify import slugify

# Ajuste BASE_DIR para apontar para a pasta raiz do repositório
BASE_DIR     = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "template_app"
DEST_ROOT    = BASE_DIR / "empresas"

# Arquivos que terão placeholders substituídos
PLACEHOLDER_FILES = [
    "pubspec.yaml",
    os.path.join("lib", "main.dart"),
    os.path.join("lib", "pages", "login_page.dart"),
    os.path.join("android", "app", "build.gradle"),
    os.path.join("ios", "Runner", "Info.plist"),
]

def prepare_project(company_name: str, bundle_id: str) -> str:
    """
    1) Gera slug a partir do nome da empresa
    2) Copia todo o template_app/ → empresas/<slug>/
    3) Substitui {{APP_SLUG}}, {{APP_NAME}} e {{BUNDLE_ID}} nos arquivos listados
    4) Retorna o slug gerado
    """
    slug = slugify(company_name, lowercase=True)
    dest = DEST_ROOT / slug

    # Se já existe, remove para recriar
    if dest.exists():
        shutil.rmtree(dest)

    # Copia árvore de arquivos
    shutil.copytree(TEMPLATE_DIR, dest)

    # Faz o replace de placeholders
    placeholders = {
        "{{APP_SLUG}}": slug,
        "{{APP_NAME}}": company_name,
        "{{BUNDLE_ID}}": bundle_id,
    }

    for rel_path in PLACEHOLDER_FILES:
        file_path = dest / rel_path
        if not file_path.is_file():
            continue
        content = file_path.read_text(encoding="utf-8")
        for key, val in placeholders.items():
            content = content.replace(key, val)
        file_path.write_text(content, encoding="utf-8")

    return slug
