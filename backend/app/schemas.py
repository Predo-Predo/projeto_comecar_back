# backend/app/schemas.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# --- Empresa schemas ---

class EmpresaBase(BaseModel):
    nome: str
    cnpj: str
    email_contato: str
    telefone: str
    logo_empresa_url: Optional[str] = None
    play_service_account_json: Optional[str] = None  # ← novo campo

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Projeto schemas ---

class ProjetoBase(BaseModel):
    nome: str
    repo_url: str
    descricao: Optional[str] = None

class ProjetoCreate(ProjetoBase):
    pass

class Projeto(ProjetoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- App schemas ---

class AppBase(BaseModel):
    empresa_id: int
    logo_app_url: Optional[str] = None
    google_service_json: Optional[dict] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_issuer_id: Optional[str] = None
    projeto_id: int

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    app_key: str
    bundle_id: Optional[str] = None
    package_name: Optional[str] = None
    esta_ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True
