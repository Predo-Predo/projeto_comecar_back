from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean, func
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

    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    user             = relationship("User", back_populates="empresas")

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

    id             = Column(Integer, primary_key=True, index=True)
    empresa_id     = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    projeto_id     = Column(Integer, ForeignKey("projetos.id"), nullable=False)

    nome           = Column(Text, nullable=False)
    descricao      = Column(Text, nullable=False)
    logo_app       = Column(Text, nullable=True)
    package_name   = Column(Text, nullable=True)
    esta_ativo     = Column(Boolean, nullable=False, default=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa", back_populates="apps")
    projeto = relationship("Projeto", back_populates="apps")


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(Text, unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=True)
    nome            = Column(Text, nullable=True)
    oauth_provider  = Column(Text, nullable=True)
    oauth_sub       = Column(Text, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    empresas        = relationship("Empresa", back_populates="user")
