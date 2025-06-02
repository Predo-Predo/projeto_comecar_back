from datetime import datetime
from typing import Optional
from pydantic import BaseModel, conint

# --- Empresa schemas ---

class EmpresaBase(BaseModel):
    name: str
    cnpj: str
    email_contact: str
    phone: str
    logo_url: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --- App schemas ---

class AppBase(BaseModel):
    company_id: int
    logo_url: Optional[str] = None
    app_key: Optional[str] = None
    bundle_id: Optional[str] = None
    package_name: Optional[str] = None
    google_service_json: Optional[dict] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_issuer_id: Optional[str] = None

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
