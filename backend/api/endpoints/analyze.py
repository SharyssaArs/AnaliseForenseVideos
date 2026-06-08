# backend/api/endpoints/analyze.py

from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.services.video_validator import validate
from backend.services.hash_service import (
    calculate_sha256,
    check_cache
)

from backend.core.database import get_db

# TODO (issue banco)
# from backend.database.session import get_db
# from backend.models.analysis import Analysis

# TODO (issue celery)
# from backend.workers.tasks import process_analysis

router = APIRouter()

BASE_UPLOAD_DIR = Path("uploads")


@router.post(
    "/analyze",
    status_code=status.HTTP_202_ACCEPTED
)
async def analyze(
    file: UploadFile = File(...)
):
    """
    POST /analyze

    Fluxo:

    1. Recebe UploadFile
    2. Salva temporariamente
    3. Valida vídeo
    4. Calcula SHA-256
    5. Verifica cache
    6. Cria registro em analises
    7. Enfileira tarefa Celery
    """

    BASE_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_filename = (
        f"{uuid4()}_{file.filename}"
    )

    temp_path = (
        BASE_UPLOAD_DIR / temp_filename
    )

    try:

        # ==========================
        # Salva arquivo
        # ==========================

        with open(temp_path, "wb") as buffer:

            while chunk := await file.read(
                1024 * 1024
            ):
                buffer.write(chunk)

        # ==========================
        # Validação
        # ==========================

        validation = validate(
            str(temp_path),
            file.filename
        )

        if not validation["is_valid"]:

            temp_path.unlink(
                missing_ok=True
            )

            errors = validation["errors"]

            error_message = (
                errors[0]
                if errors
                else "Arquivo inválido."
            )

            if (
                "extensão" in error_message.lower()
                or "invalida" in error_message.lower()
                or "inválida" in error_message.lower()
            ):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "INVALID_FORMAT",
                            "message": error_message
                        }
                    }
                )

            if (
                "arquivo muito grande"
                in error_message.lower()
            ):
                raise HTTPException(
                    status_code=413,
                    detail={
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": error_message
                        }
                    }
                )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_VIDEO",
                        "message": error_message
                    }
                }
            )

        file_hash = calculate_sha256(
            str(temp_path)
        )

        # ==========================
        # Cache
        # ==========================

        with get_db() as db:

            cached_analysis = check_cache(
                file_hash,
                db
            )

            if cached_analysis:

                return {
                    "task_id": str(
                        cached_analysis.task_id
                    ),
                    "status":
                        cached_analysis.status,
                    "cached": True
                }

        task_id = str(uuid4())

        created_at = datetime.now(
            timezone.utc
        )

        # ==========================
        # Banco
        # ==========================

        # TODO (issue banco)


        # ==========================
        # Celery
        # ==========================

        # TODO (issue celery)

        return {
            "task_id": task_id,
            "status": "pending",
            "created_at":
                created_at.isoformat()
        }

    except HTTPException:
        raise

    except Exception as exc:

        temp_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code":
                        "INTERNAL_SERVER_ERROR",
                    "message": str(exc)
                }
            }
        )
