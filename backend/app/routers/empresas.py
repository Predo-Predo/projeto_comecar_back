# backend/app/routers/empresas.py

import os
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

    # Se fornecido, grava o JSON de credenciais do Google Play em disco
    if emp.play_service_account_json:
        caminho = os.path.join("play_creds", f"{nova.id}.json")
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(emp.play_service_account_json)

    return nova


@router.get(
    "/",
    response_model=list[schemas.Empresa]
)
def listar_empresas(db: Session = Depends(database.get_db)):
    return db.query(models.Empresa).order_by(models.Empresa.created_at.desc()).all()
