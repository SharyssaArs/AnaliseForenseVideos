import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.core.database import Base


class LogProcessamento(Base):
    __tablename__ = "logs_processamento"

    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    analise_id = Column(
        CHAR(36),
        ForeignKey("analises.id"),
        nullable=False
    )

    etapa = Column(
        String(100),
        nullable=False
    )

    status = Column(
        SQLEnum(
            "iniciado",
            "sucesso",
            "erro"
        ),
        nullable=False
    )

    mensagem = Column(
        Text,
        nullable=True
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    analise = relationship(
        "Analise",
        back_populates="logs"
    )


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analise_id: str
    etapa: str
    status: str
    mensagem: str | None = None
    criado_em: datetime