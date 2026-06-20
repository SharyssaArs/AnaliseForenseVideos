from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.analise import Analise

from backend.api.dependencies.auth import get_current_user

router = APIRouter()


@router.delete("/analysis/{task_id}")
def cancel_analysis(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):

    analise = (
        db.query(Analise)
        .filter(Analise.task_id == task_id)
        .first()
    )

    if analise is None:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada"
        )

    # TODO(AUTH):
    # Quando a autenticação estiver implementada,
    # verificar se:
    #
    # current_user.id == analise.user_id
    #
    # Caso contrário:
    #
    # raise HTTPException(
    #     status_code=403,
    #     detail="Forbidden"
    # )
    #

    if analise.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "ANALYSIS_NOT_CANCELLABLE",
                    "message": (
                        f"Análise com status "
                        f"'{analise.status}' "
                        f"não pode ser cancelada"
                    )
                }
            }
        )

    # TODO(CELERY):
    # Quando o Celery estiver configurado:
    #
    # from backend.workers.celery_app import celery_app
    #
    # celery_app.control.revoke(
    #     analise.task_id,
    #     terminate=True
    # )
    #

    analise.status = "failed"

    # TODO(ERROR_MESSAGE):
    # A issue exige:
    #
    # "Analise cancelada pelo usuario"
    #
    # Porém atualmente:
    # - não existe coluna error_message
    # - não existe migration correspondente
    #
    # Quando a coluna existir:
    #
    # analise.error_message = (
    #     "Analise cancelada pelo usuario"
    # )

    db.commit()
    db.refresh(analise)

    return {
        "message": "Análise cancelada com sucesso",
        "task_id": analise.task_id,
        "status": analise.status,
    }
