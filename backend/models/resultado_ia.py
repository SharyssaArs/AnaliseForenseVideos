import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Numeric
from sqlalchemy.orm import relationship

from backend.core.database import Base


class ResultadoIA(Base):
    __tablename__ = "resultados_ia"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    analise_id = Column(
        CHAR(36),
        ForeignKey("analises.id"),
        unique=True,
        nullable=False,
    )

    score_confianca = Column(
        Numeric(5, 4),
        nullable=False,
    )

    classificacao = Column(
        SQLEnum(
            "REAL",
            "MANIPULADO",
        ),
        nullable=False,
    )

    detalhes_json = Column(JSON, nullable=True)

    finalizado_em = Column(DateTime, nullable=True)

    criado_em = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    analise = relationship(
        "Analise",
        back_populates="resultado_ia"
    )


class ResultadoIAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analise_id: str
    score_confianca: float
    classificacao: str
    detalhes_json: Optional[Dict[str, Any]] = None
    finalizado_em: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: datetime