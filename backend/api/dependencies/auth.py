import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)


def verify_internal_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente."
        )

    expected_token = os.getenv("INTERNAL_API_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token interno não configurado no servidor."
        )

    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido."
        )

    return credentials.credentials


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    return verify_internal_token(credentials)
