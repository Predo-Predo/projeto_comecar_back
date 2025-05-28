import os
import shutil
from slugify import slugify

# ---------------------------------------------------
# Resolve caminhos absolutos a partir deste arquivo
# ---------------------------------------------------
THIS_FILE = os.path.abspath(__file__)
APP_DIR   = os.path.dirname(THIS_FILE)       # backend/app
BACKEND   = os.path.dirname(APP_DIR)         # backend
ROOT_DIR  = os.path.dirname(BACKEND)         # raiz do projeto

# ---------------------------------------------------
# Diretórios de template e destino
# ---------------------------------------------------
TEMPLATE_DIR = os.path.join(ROOT_DIR, "template_app")
DEST_ROOT    = os.path.join(ROOT_DIR, "empresas")

# ---------------------------------------------------
# Arquivos onde faremos placeholder replacement
# ---------------------------------------------------
PLACEHOLDER_FILES = [
    "pubspec.yaml",
    os.path.join("lib", "main.dart"),
    os.path.join("lib", "pages", "login_page.dart"),
    os.path.join("android", "app", "build.gradle"),
    os.path.join("ios", "Runner", "Info.plist"),
]

def prepare_project(company_id: int, company_name: str, bundle_id: str) -> str:
    """
    1) Gera slug (ex: "minha-empresa")
    2) Monta pasta destino como: empresas/{company_id}-{slug}/
    3) Copia template_app → empresas/{company_id}-{slug}/ (se ainda não existir)
    4) Substitui {{APP_SLUG}}, {{APP_NAME}}, {{BUNDLE_ID}}
    5) Retorna o nome da pasta criada (ex: "5-minha-empresa")
    """
    # 1) cria slug
    slug = slugify(company_name, lowercase=True)

    # 2) nome único por empresa
    folder_name = f"{company_id}-{slug}"
    dest = os.path.join(DEST_ROOT, folder_name)

    # 3) copia apenas se não existir
    if not os.path.exists(dest):
        shutil.copytree(TEMPLATE_DIR, dest)

    # 4) placeholders
    placeholders = {
        "{{APP_SLUG}}": slug,
        "{{APP_NAME}}": company_name,
        "{{BUNDLE_ID}}": bundle_id,
    }

    for rel_path in PLACEHOLDER_FILES:
        file_path = os.path.join(dest, rel_path)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        for key, val in placeholders.items():
            content = content.replace(key, val)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return folder_name
