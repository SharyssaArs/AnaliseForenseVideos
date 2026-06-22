from datetime import timedelta

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.endpoints.auth import router as auth_router
from backend.core.database import Base, get_db_session
from backend.core.security import create_access_token, get_current_user
from backend.models import analise, log_processamento, resultado_ia  # noqa: F401
from backend.models.usuario import Usuario


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db


@app.get("/protected")
def protected(user: Usuario = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_user(email="user@example.com", password="password123"):
    return client.post(
        "/auth/register",
        json={"nome": "Test User", "email": email, "password": password},
    )


def test_register_hashes_password_and_rejects_duplicate_email():
    response = register_user(email="User@Example.com")
    assert response.status_code == 201

    with TestingSession() as db:
        user = db.query(Usuario).one()
        assert user.email == "user@example.com"
        assert user.senha_hash != "password123"
        assert user.senha_hash.startswith("$2")

    duplicate = register_user(email="USER@example.com")
    assert duplicate.status_code == 409


def test_login_returns_bearer_token_and_valid_token_authenticates():
    register_user()
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]
    claims = jwt.decode(token, options={"verify_signature": False})
    assert claims["exp"] - claims["iat"] == 24 * 60 * 60

    protected_response = client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == 200
    assert protected_response.json()["email"] == "user@example.com"


def test_login_with_wrong_password_returns_401():
    register_user()
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_expired_token_returns_401_on_protected_endpoint():
    register_user()
    with TestingSession() as db:
        user = db.query(Usuario).one()
        token = create_access_token(user.id, expires_delta=timedelta(seconds=-1))

    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
