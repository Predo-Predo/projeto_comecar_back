from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from .routers import empresas, apps, templates

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Empresas/Apps/Builds")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inclusão dos routers organizados
app.include_router(empresas.router)
app.include_router(apps.router)
app.include_router(templates.router)
