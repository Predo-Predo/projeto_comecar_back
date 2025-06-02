from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=schemas.Template, status_code=status.HTTP_201_CREATED)
def criar_template(template: schemas.TemplateCreate, db: Session = Depends(database.get_db)):
    existe = db.query(models.Template).filter(models.Template.repo_url == template.repo_url).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este repositório já está cadastrado como template.")
    
    novo = models.Template(**template.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
