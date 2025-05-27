import os
import shutil
from slugify import slugify

# Caminhos relativos à raiz do repositório
TEMPLATE_DIR = "template_app"
DEST_ROOT   = "empresas"

# Arquivos que terão placeholders substituídos
PLACEHOLDER_FILES = [
    "pubspec.yaml",
    os.path.join("lib", "main.dart"),
    os.path.join("lib", "pages", "login_page.dart"),  # caso queira substituir textos
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
    dest = os.path.join(DEST_ROOT, slug)

    # Se já existe, remove para recriar
    if os.path.exists(dest):
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
        path = os.path.join(dest, rel_path)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for key, val in placeholders.items():
            content = content.replace(key, val)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    return slug
