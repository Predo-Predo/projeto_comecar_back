from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime

# -------------------
# Empresa schemas
# -------------------

class EmpresaBase(BaseModel):
    name: str
    cnpj: str
    email_contact: EmailStr
    phone: str
    logo_url: Optional[str] = None
    app_key: Optional[str] = None
    bundle_id: Optional[str] = None
    package_name: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_issuer_id: Optional[str] = None
    google_service_json: Optional[Any] = None

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------
# App schemas
# -------------------

class AppCreate(BaseModel):
    company_id: int

class App(AppCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------
# Build schemas
# -------------------

class BuildCreate(BaseModel):
    company_id: int

class Build(BaseModel):
    id: int
    company_id: int
    workflow_run_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
