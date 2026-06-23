import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Analise(Base):
    __tablename__ = "analises"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("usuarios.id"), nullable=True)
    task_id = Column(String(100), nullable=False)
    video_hash = Column(String(64), unique=True, nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    status = Column(
        SQLEnum("pending", "processing", "completed", "failed"),
        default="pending",
        nullable=False,
    )
    progress = Column(Integer, default=0, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="analises")

    resultado_ia = relationship(
        "ResultadoIA",
        back_populates="analise",
        uselist=False,
        cascade="all, delete-orphan",
    )

    logs = relationship(
        "LogProcessamento",
        back_populates="analise",
        cascade="all, delete-orphan",
    )


class AnaliseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    task_id: str
    video_hash: str
    nome_arquivo: str
    status: str
    progress: int
    criado_em: datetime
    atualizado_em: datetime
