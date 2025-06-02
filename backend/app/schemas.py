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

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Template schemas ---

class TemplateBase(BaseModel):
    nome: str
    repo_url: str
    descricao: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- App schemas ---

class AppBase(BaseModel):
    empresa_id: int
    logo_url: Optional[str] = None
    google_service_json: Optional[dict] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_issuer_id: Optional[str] = None
    template_id: int

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    app_key: Optional[str]
    bundle_id: Optional[str]
    package_name: Optional[str]
    esta_ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True
