from fastapi import APIRouter, HTTPException

from backend.core.database import get_db
from backend.models.analise import Analise
from backend.models.resultado_ia import ResultadoIA

from backend.api.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/result/{task_id}")
def get_result(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    analise = (
        db.query(Analise)
        .filter(Analise.task_id == task_id)
        .first()
    )

    with get_db() as db:

        analise = (
            db.query(Analise)
            .filter(Analise.task_id == task_id)
            .first()
        )

        if analise is None:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada",
            )

        if analise.status in ["pending", "processing"]:
            raise HTTPException(
                status_code=404,
                detail="Resultado ainda não disponível",
            )

        if analise.status == "failed":
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "TASK_FAILED",
                        "message": "A análise falhou",
                    }
                },
            )

        resultado = (
            db.query(ResultadoIA)
            .filter(ResultadoIA.analise_id == analise.id)
            .first()
        )

        if resultado is None:
            raise HTTPException(
                status_code=404,
                detail="Resultado não encontrado",
            )

        detalhes = resultado.detalhes_json or {}

        return {
            "task_id": analise.task_id,
            "is_deepfake": resultado.classificacao == "MANIPULADO",
            "confidence_score": float(resultado.score_confianca),
            "manipulation_type": detalhes.get("manipulation_type"),
            "audio_sync": detalhes.get("audio_sync"),
            "metadata_flags": detalhes.get("metadata_flags"),
            "forensic_details": detalhes.get("forensic_details"),
            "scores_breakdown": detalhes.get("scores_breakdown", {}),
            "video_info": detalhes.get("video_info", {}),
        }