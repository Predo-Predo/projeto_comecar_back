# backend/app/routers/empresas.py

import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas, database

router = APIRouter(prefix="/empresas", tags=["empresas"])

@router.post(
    "/",
    response_model=schemas.Empresa,
    status_code=status.HTTP_201_CREATED
)
async def create_empresa(
    nome: str = Form(...),
    cnpj: str = Form(...),
    email_contato: str = Form(...),
    telefone: str = Form(...),
    logo_empresa: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    # Verifica se já existe empresa com o mesmo CNPJ
    exists = db.query(models.Empresa).filter(models.Empresa.cnpj == cnpj).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa com este CNPJ já cadastrada"
        )

    # Salva o arquivo de logo em disco
    logos_dir = os.path.join(os.getcwd(), "logos")
    os.makedirs(logos_dir, exist_ok=True)
    filename = f"{uuid4().hex}_{logo_empresa.filename}"
    full_path = os.path.join(logos_dir, filename)
    contents = await logo_empresa.read()
    with open(full_path, "wb") as f:
        f.write(contents)

    # Cria nova empresa usando os campos de formulário
    nova = models.Empresa(
        nome             = nome,
        cnpj             = cnpj,
        email_contato    = email_contato,
        telefone         = telefone,
        logo_empresa     = full_path
    )
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
