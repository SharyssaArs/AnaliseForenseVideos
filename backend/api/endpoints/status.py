from uuid import UUID
from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.core.database import get_db

from backend.crud import (
    get_analise_by_task_id,
)

router = APIRouter()

@router.get("/status/{task_id}")
async def get_status( task_id: str ):
    try:
        UUID(task_id)

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_TASK_ID",
                    "message": "Invalid task_id format"
                }
            }
        )

    try:

        with get_db() as db:

            analise = get_analise_by_task_id(
                db,
                task_id
            )

            if analise is None:

                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": {
                            "code": "TASK_NOT_FOUND",
                            "message": "Task not found"
                        }
                    }
                )

            status_messages = {
                "pending": (
                    "Análise aguardando processamento"
                ),
                "processing": (
                    "Análise em processamento"
                ),
                "completed": (
                    "Análise concluída com sucesso"
                ),
                "failed": (
                    "Falha durante o processamento"
                ),
            }

            response = {
                "task_id": analise.task_id,
                "status": analise.status,
                "progress": analise.progress,
                "message": status_messages.get(
                    analise.status,
                    "Status desconhecido"
                ),
                "created_at": (
                    analise.criado_em.isoformat()
                ),
                "updated_at": (
                    analise.atualizado_em.isoformat()
                ),
            }

            if analise.status == "failed":
                response["error_message"] = (
                    "Falha durante o processamento"
                )

            return response

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": (
                        "INTERNAL_SERVER_ERROR"
                    ),
                    "message": str(exc)
                }
            }
        )