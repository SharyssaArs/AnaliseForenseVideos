from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
)

from backend.core.database import get_db
from backend.api.dependencies.auth import get_current_user

from backend.crud import (
    get_analise_by_task_id,
    get_history_by_user,
    get_logs_by_analise_id,
)

router = APIRouter()

@router.get("/history")
async def get_history(
    page: int = 1,
    limit: int = 10,
    current_user: str = Depends(get_current_user),
):

    try:
        # TODO(auth):
        # Substituir quando JWT estiver implementado.
        #
        # Exemplo futuro:
        #
        # current_user = get_current_user(...)
        # user_id = current_user.id

        user_id = "TEMP_USER_ID"

        with get_db() as db:

            analyses = get_history_by_user(
                db,
                user_id,
                page,
                limit,
            )

            return [
                {
                    "task_id":
                        analise.task_id,

                    "status":
                        analise.status,

                    "nome_arquivo":
                        analise.nome_arquivo,

                    "criado_em":
                        analise.criado_em.isoformat(),
                }
                for analise in analyses
            ]

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code":
                        "INTERNAL_SERVER_ERROR",
                    "message":
                        str(exc),
                }
            },
        )
    
@router.get("/analysis/{task_id}")
async def get_analysis(
    task_id: str,
    current_user: str = Depends(get_current_user),
):

    try:

        with get_db() as db:

            analise = (
                get_analise_by_task_id(
                    db,
                    task_id,
                )
            )

            if analise is None:

                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": {
                            "code":
                                "TASK_NOT_FOUND",
                            "message":
                                "Task not found",
                        }
                    },
                )

            logs = get_logs_by_analise_id(
                db,
                analise.id,
            )

            duration = int(
                (
                    analise.atualizado_em
                    - analise.criado_em
                ).total_seconds()
            )

            return {
                "task_id":
                    analise.task_id,

                "nome_arquivo":
                    analise.nome_arquivo,

                "status":
                    analise.status,

                "duration":
                    duration,

                "logs": [
                    {
                        "etapa":
                            log.etapa,

                        "status":
                            log.status,

                        "mensagem":
                            log.mensagem,

                        "criado_em":
                            log.criado_em.isoformat(),
                    }
                    for log in logs
                ],
            }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code":
                        "INTERNAL_SERVER_ERROR",
                    "message":
                        str(exc),
                }
            },
        )
