import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Lê a URL do banco (configure no seu .env)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Variável DATABASE_URL não encontrada no .env")

# Cria o engine e a fábrica de sessões
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para todos os models
Base = declarative_base()

# ✅ Adicione esta função para uso com Depends()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
