# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from . import models
from .database import engine
from .routers import empresas, apps, projetos, auth, users
from app.config import settings

app = FastAPI(title="API de Empresas/Apps/Builds")

# --- Sessions (necessário para OAuth) ---
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
)
# ------------------------

# --- CORS restrito novamente ---
origins = [
    "http://localhost:59598",                       # seu front local em dev
    "https://3213-177-129-251-249.ngrok-free.app",  # URL do túnel HTTPS
    "https://predo-predo.github.io",                # domínio root GitHub Pages
    "https://predo-predo.github.io/projeto_comecar_back",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# inclusão dos routers existentes
app.include_router(empresas.router)
app.include_router(apps.router)
app.include_router(projetos.router)
app.include_router(auth.router)
app.include_router(users.router)
