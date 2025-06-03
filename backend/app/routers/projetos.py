# backend/app/routers/projetos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/projetos", tags=["projetos"])


@router.post(
    "/",
    response_model=schemas.Projeto,
    status_code=status.HTTP_201_CREATED
)
def criar_projeto(
    projeto: schemas.ProjetoCreate,
    db: Session = Depends(database.get_db),
):
    existe = db.query(models.Projeto).filter(models.Projeto.repo_url == projeto.repo_url).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esse repositório já está cadastrado como projeto."
        )

    novo = models.Projeto(**projeto.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get(
    "/",
    response_model=list[schemas.Projeto]
)
def listar_projetos(db: Session = Depends(database.get_db)):
    return db.query(models.Projeto).order_by(models.Projeto.created_at.desc()).all()
