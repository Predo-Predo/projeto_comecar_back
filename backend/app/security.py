# backend/app/security.py

import time
from typing import Dict, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth

from app.config import settings

# --- Password hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Recebe senha em texto puro e retorna o hash bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash armazenado.
    """
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT tokens ---

def create_access_token(data: Dict[str, str]) -> str:
    """
    Gera um JWT de acesso com payload 'data' e expiração configurada.
    """
    to_encode = data.copy()
    expire = int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> Optional[Dict]:
    """
    Decodifica e valida um JWT; retorna o payload se válido, ou None se inválido.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# --- OAuth2 / OIDC setup (Google & Apple) ---

oauth = OAuth()

# Google OIDC
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Apple Sign-In (OIDC)
# Para Apple você precisa gerar um client_secret JWT assinado com sua chave .p8
def _apple_client_secret() -> str:
    now = int(time.time())
    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": now,
        "exp": now + 86400 * 180,      # válido por até 180 dias
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }
    headers = {"kid": settings.APPLE_KEY_ID}
    return jwt.encode(payload, settings.APPLE_PRIVATE_KEY, algorithm="ES256", headers=headers)

oauth.register(
    name="apple",
    client_id=settings.APPLE_CLIENT_ID,
    client_secret=_apple_client_secret,
    server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email name"},
)
