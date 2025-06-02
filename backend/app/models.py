from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(Text, nullable=False)
    cnpj           = Column(Text, nullable=False, unique=True)
    email_contato  = Column(Text, nullable=False)
    telefone          = Column(Text, nullable=False)
    logo_empresa_url       = Column(Text, nullable=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    apps = relationship("App", back_populates="empresa")


class Template(Base):
    __tablename__ = "templates"

    id          = Column(Integer, primary_key=True, index=True)
    nome        = Column(Text, nullable=False)
    repo_url    = Column(Text, nullable=False)
    descricao   = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=False), server_default=func.now())


class App(Base):
    __tablename__ = "apps"

    id                  = Column(Integer, primary_key=True, index=True)
    company_id          = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    logo_url            = Column(Text, nullable=True)
    app_key             = Column(Text, nullable=True)
    bundle_id           = Column(Text, nullable=True)
    package_name        = Column(Text, nullable=True)
    google_service_json = Column(JSON, nullable=True)
    apple_team_id       = Column(Text, nullable=True)
    apple_key_id        = Column(Text, nullable=True)
    apple_issuer_id     = Column(Text, nullable=True)
    template_id         = Column(Integer, ForeignKey("templates.id"), nullable=False)
    esta_ativo          = Column(Boolean, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa", back_populates="apps")
