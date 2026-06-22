import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from backend.core.database import get_db_session
from backend.models.usuario import Usuario

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = 24
bearer_scheme = HTTPBearer(auto_error=False)


def _secret_key() -> str:
    return os.getenv("SECRET_KEY", "change-this-secret-key-in-production")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": expires_at},
        _secret_key(),
        algorithm=ALGORITHM,
    )


def _unauthorized(detail: str = "Token invalido ou expirado.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db_session),
) -> Usuario:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Token de autenticacao ausente.")

    try:
        payload = jwt.decode(
            credentials.credentials,
            _secret_key(),
            algorithms=[ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise _unauthorized()
    except ExpiredSignatureError as exc:
        raise _unauthorized("Token expirado.") from exc
    except InvalidTokenError as exc:
        raise _unauthorized() from exc

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise _unauthorized()
    return user
