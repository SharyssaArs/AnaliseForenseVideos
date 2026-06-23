from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.analise import Analise
from backend.models.resultado_ia import ResultadoIA


router = APIRouter()


@router.get("/result/{task_id}")
def get_result(
    task_id: str,
    db: Session = Depends(get_db),
):
    analise = db.query(Analise).filter(Analise.task_id == task_id).first()

    if analise is None:
        raise HTTPException(status_code=404, detail="Analise nao encontrada")

    if analise.status in ["pending", "processing"]:
        raise HTTPException(status_code=404, detail="Resultado ainda nao disponivel")

    if analise.status == "failed":
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "TASK_FAILED",
                    "message": "A analise falhou",
                }
            },
        )

    resultado = (
        db.query(ResultadoIA)
        .filter(ResultadoIA.analise_id == analise.id)
        .first()
    )

    if resultado is None:
        raise HTTPException(status_code=404, detail="Resultado nao encontrado")

    detalhes = resultado.detalhes_json or {}
    scores_breakdown = detalhes.get("scores_breakdown") or detalhes.get("layer_scores") or {}

    return {
        "task_id": analise.task_id,
        "analysis_id": analise.id,
        "status": analise.status,
        "progress": analise.progress,
        "filename": analise.nome_arquivo,
        "video_hash": analise.video_hash,
        "is_deepfake": resultado.classificacao == "MANIPULADO",
        "classification": resultado.classificacao,
        "confidence_score": float(resultado.score_confianca),
        "manipulation_type": detalhes.get("manipulation_type"),
        "audio_sync": detalhes.get("audio_sync"),
        "metadata_flags": detalhes.get("metadata_flags") or [],
        "forensic_details": detalhes.get("forensic_details"),
        "scores_breakdown": scores_breakdown,
        "layer_scores": scores_breakdown,
        "video_info": detalhes.get("video_info", {}),
        "created_at": analise.criado_em.isoformat(),
        "completed_at": (
            resultado.finalizado_em.isoformat()
            if resultado.finalizado_em
            else None
        ),
    }
