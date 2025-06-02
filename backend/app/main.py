from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Empresas/Apps/Builds")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Rotas Empresa ---

@app.post("/empresas/", response_model=schemas.Empresa, status_code=201)
def criar_empresa(dados: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Empresa).filter(models.Empresa.cnpj == dados.cnpj).first()
    if existe:
        raise HTTPException(400, "CNPJ já cadastrado")
    empresa = models.Empresa(**dados.dict())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

# (outras rotas...)

# --- Rotas App ---

@app.post("/apps/", response_model=schemas.App, status_code=201)
def criar_app(dados: schemas.AppCreate, db: Session = Depends(get_db)):
    # opcional: validar se company_id existe
    empresa = db.query(models.Empresa).get(dados.company_id)
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")
    app_obj = models.App(**dados.dict())
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@app.get("/apps/", response_model=list[schemas.App])
def listar_apps(db: Session = Depends(get_db)):
    return db.query(models.App).order_by(models.App.created_at.desc()).all()
