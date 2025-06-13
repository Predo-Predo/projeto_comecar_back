# backend/app/config.py

import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    # Google OAuth2 / OIDC
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    # Apple Sign-In (OIDC) – ignoramos por enquanto, mas já deixamos aqui
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID")
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID")
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID")
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY")

# Instância única de settings
settings = Settings()
