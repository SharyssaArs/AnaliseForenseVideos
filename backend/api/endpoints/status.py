from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud import get_analise_by_task_id


router = APIRouter()


@router.get("/status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    try:
        UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_TASK_ID",
                    "message": "Invalid task_id format",
                }
            },
        )

    try:
        analise = get_analise_by_task_id(db, task_id)

        if analise is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": "Task not found",
                    }
                },
            )

        status_messages = {
            "pending": "Analise aguardando processamento",
            "processing": "Analise em processamento",
            "completed": "Analise concluida com sucesso",
            "failed": "Falha durante o processamento",
        }

        response = {
            "task_id": analise.task_id,
            "status": analise.status,
            "progress": analise.progress,
            "message": status_messages.get(analise.status, "Status desconhecido"),
            "analysis": {
                "id": analise.id,
                "task_id": analise.task_id,
                "video_hash": analise.video_hash,
                "nome_arquivo": analise.nome_arquivo,
                "status": analise.status,
                "progress": analise.progress,
                "created_at": analise.criado_em.isoformat(),
                "updated_at": analise.atualizado_em.isoformat(),
            },
            "created_at": analise.criado_em.isoformat(),
            "updated_at": analise.atualizado_em.isoformat(),
        }

        if analise.status == "failed":
            response["error_message"] = "Falha durante o processamento"

        return response

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                }
            },
        )
