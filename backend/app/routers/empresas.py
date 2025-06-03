# backend/app/routers/empresas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.post(
    "/",
    response_model=schemas.Empresa,
    status_code=status.HTTP_201_CREATED
)
def create_empresa(
    emp: schemas.EmpresaCreate,
    db: Session = Depends(database.get_db),
):
    # Verifica se já existe empresa com o mesmo CNPJ
    exists = db.query(models.Empresa).filter(models.Empresa.cnpj == emp.cnpj).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa com este CNPJ já cadastrada"
        )

    # Cria nova empresa usando emp.dict()
    nova = models.Empresa(**emp.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.get(
    "/",
    response_model=list[schemas.Empresa]
)
def listar_empresas(db: Session = Depends(database.get_db)):
    return db.query(models.Empresa).order_by(models.Empresa.created_at.desc()).all()
