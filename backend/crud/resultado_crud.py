from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.models.analise import Analise
from backend.models.resultado_ia import ResultadoIA


def create_resultado_ia(
    db: Session,
    analise_id: str,
    score_confianca: float,
    classificacao: str,
    detalhes_json: dict[str, Any] | None = None,
):
    resultado = ResultadoIA(
        analise_id=analise_id,
        score_confianca=score_confianca,
        classificacao=classificacao,
        detalhes_json=detalhes_json,
        finalizado_em=datetime.utcnow(),
    )

    db.add(resultado)
    db.commit()
    db.refresh(resultado)

    return resultado


def get_resultado_by_analise_id(
    db: Session,
    analise_id: str,
):
    analise = (
        db.query(Analise)
        .filter(Analise.id == analise_id)
        .first()
    )

    if analise is None:
        return None

    if analise.status != "completed":
        return None

    return (
        db.query(ResultadoIA)
        .filter(ResultadoIA.analise_id == analise_id)
        .first()
    )