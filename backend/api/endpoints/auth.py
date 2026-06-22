from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.database import get_db_session
from backend.core.security import create_access_token, hash_password, verify_password
from backend.crud.usuario_crud import get_usuario_by_email
from backend.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RegisteredUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    email: str


def _normalized_email(email: str) -> str:
    return email.strip().lower()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    user = get_usuario_by_email(db, _normalized_email(payload.email))
    if user is None or not verify_password(payload.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha invalidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/register", response_model=RegisteredUserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    email = _normalized_email(payload.email)
    if get_usuario_by_email(db, email) is not None:
        raise HTTPException(status_code=409, detail="Ja existe um usuario com este email.")

    try:
        user = Usuario(
            nome=payload.nome.strip(),
            email=email,
            senha_hash=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe um usuario com este email.",
        ) from exc
    return user
