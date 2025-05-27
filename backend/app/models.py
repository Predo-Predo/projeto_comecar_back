from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    TIMESTAMP,
    JSON,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from .database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    cnpj = Column(String(18), nullable=False, unique=True, index=True)
    email_contact = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    logo_url = Column(Text, nullable=True)
    app_key = Column(Text, nullable=True)
    bundle_id = Column(Text, nullable=True)
    package_name = Column(Text, nullable=True)
    apple_team_id = Column(Text, nullable=True)
    apple_key_id = Column(Text, nullable=True)
    apple_issuer_id = Column(Text, nullable=True)
    google_service_json = Column(JSON, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # relacionamentos
    apps   = relationship("App",   back_populates="empresa")
    builds = relationship("Build", back_populates="empresa")


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    repo_url = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    empresa = relationship("Empresa", back_populates="apps")


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    workflow_run_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    empresa = relationship("Empresa", back_populates="builds")
