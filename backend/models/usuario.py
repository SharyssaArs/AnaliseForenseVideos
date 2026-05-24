import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import CHAR, Column, DateTime, String
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    analises = relationship(
        "Analise",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: str
    criado_em: datetime
    atualizado_em: datetime