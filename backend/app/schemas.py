from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# --- Empresa schemas ---

class EmpresaBase(BaseModel):
    nome: str
    cnpj: str
    email_contato: str
    telefone: str
    logo_empresa: Optional[str] = None

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
    projeto_id: int
    nome: str
    descricao: str
    logo_app: Optional[str] = None
    package_name: Optional[str] = None

class AppCreate(AppBase):
    pass

class App(AppBase):
    id: int
    esta_ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth/User schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nome: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nome: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None


# ———— novo schema para login ————

class UserLogin(BaseModel):
    email: EmailStr
    password: str
