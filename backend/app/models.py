# backend/app/models.py

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id               = Column(Integer, primary_key=True, index=True)
    nome             = Column(Text, nullable=False)
    cnpj             = Column(Text, nullable=False, unique=True)
    email_contato    = Column(Text, nullable=False)
    telefone         = Column(Text, nullable=False)
    logo_empresa     = Column(Text, nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    apps = relationship("App", back_populates="empresa")


class Projeto(Base):
    __tablename__ = "projetos"

    id          = Column(Integer, primary_key=True, index=True)
    nome        = Column(Text, nullable=False)
    repo_url    = Column(Text, nullable=False, unique=True)
    descricao   = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    apps = relationship("App", back_populates="projeto")


class App(Base):
    __tablename__ = "apps"

    id                  = Column(Integer, primary_key=True, index=True)
    empresa_id          = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    logo_app            = Column(Text, nullable=True)
    app_key             = Column(Text, nullable=False)
    bundle_id           = Column(Text, nullable=True)
    package_name        = Column(Text, nullable=True)
    google_service_json = Column(JSON, nullable=True)
    apple_team_id       = Column(Text, nullable=True)
    apple_key_id        = Column(Text, nullable=True)
    apple_issuer_id     = Column(Text, nullable=True)
    projeto_id          = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    esta_ativo          = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa", back_populates="apps")
    projeto = relationship("Projeto", back_populates="apps")


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(Text, unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=True)
    nome            = Column(Text, nullable=True)
    oauth_provider  = Column(Text, nullable=True)  # ex: "google", "apple"
    oauth_sub       = Column(Text, nullable=True)  # identificador no provedor
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
