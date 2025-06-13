# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import empresas, apps, projetos, auth, users

app = FastAPI(title="API de Empresas/Apps/Builds")

origins = [
    "http://localhost:59598",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app.include_router(empresas.router)
app.include_router(apps.router)
app.include_router(projetos.router)
app.include_router(auth.router)
app.include_router(users.router)
