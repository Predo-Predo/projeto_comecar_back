from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# ---- Base para os seus modelos ----
Base = declarative_base()

# ---- Engine assíncrono ----
engine = create_async_engine(
    settings.DATABASE_URL,  # ex: postgresql+asyncpg://user:pass@host:5432/db
    echo=True,
    future=True,
)

# ---- Sessionmaker para AsyncSession ----
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ---- Dependency para injetar o DB nas rotas ----
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
