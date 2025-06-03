# backend/app/main.py

from fastapi import FastAPI
from . import models
from .database import engine
from .routers import empresas, apps, projetos

# Cria as tabelas definidas em models.py (caso ainda não existam)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Empresas/Apps/Builds")

app.include_router(empresas.router)
app.include_router(apps.router)
app.include_router(projetos.router)
