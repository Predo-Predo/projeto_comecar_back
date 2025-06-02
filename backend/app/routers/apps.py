from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from slugify import slugify

router = APIRouter(prefix="/apps", tags=["apps"])

@router.post("/", response_model=schemas.App, status_code=status.HTTP_201_CREATED)
def create_app(app: schemas.AppCreate, db: Session = Depends(database.get_db)):
    # Verifica se empresa existe
    empresa = db.query(models.Empresa).filter(models.Empresa.id == app.company_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # Verifica se template existe
    if not hasattr(app, "template_id") or app.template_id is None:
        raise HTTPException(status_code=400, detail="template_id é obrigatório")
    template = db.query(models.Template).filter(models.Template.id == app.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")

    # Geração automática de campos
    app_key = slugify(f"{empresa.name}_{empresa.id}")
    bundle_id = f"com.{slugify(empresa.name)}.app"
    package_name = bundle_id

    novo_app = models.App(
        company_id=app.company_id,
        logo_url=app.logo_url,
        app_key=app_key,
        bundle_id=bundle_id,
        package_name=package_name,
        google_service_json=app.google_service_json,
        apple_team_id=app.apple_team_id,
        apple_key_id=app.apple_key_id,
        apple_issuer_id=app.apple_issuer_id,
        template_id=app.template_id,
        esta_ativo=True,
    )

    db.add(novo_app)
    db.commit()
    db.refresh(novo_app)
    return novo_app
