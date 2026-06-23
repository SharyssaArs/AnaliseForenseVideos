from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.analise import Analise
from backend.models.resultado_ia import ResultadoIA
from backend.services.hash_service import calculate_sha256, check_cache
from backend.services.video_validator import validate
from backend.services.metadata_analysis import analyze as analyze_metadata
from backend.services.audio_analysis import analyze as analyze_audio
from backend.services.visual_analysis import analyze as analyze_visual

router = APIRouter()

BASE_UPLOAD_DIR = Path("uploads")


def build_real_result(video_path: str, file_hash: str, filename: str) -> dict:
    metadata_result = analyze_metadata(video_path)
    audio_result = analyze_audio(video_path)
    visual_result = analyze_visual(video_path)

    visual_score = float(visual_result.get("visual_score", 0.0))
    metadata_score = float(metadata_result.get("metadata_score", 0.0))

    audio_consistency = float(audio_result.get("audio_score", 0.0))
    audio_suspicion = 1.0 - audio_consistency

    confidence_score = round(
        (visual_score * 0.45)
        + (audio_suspicion * 0.25)
        + (metadata_score * 0.30),
        4,
    )

    if visual_score >= 0.60:
        is_deepfake = confidence_score >= 0.50
    elif metadata_score >= 0.70 and audio_suspicion >= 0.60:
        is_deepfake = confidence_score >= 0.55
    else:
        is_deepfake = confidence_score >= 0.60

    if is_deepfake:
        manipulation_type = visual_result.get(
            "manipulation_type",
            "Possível manipulação por IA",
        )
    elif audio_suspicion >= 0.60 or metadata_score >= 0.60:
        manipulation_type = "Indícios técnicos de edição/recompressão"
    else:
        manipulation_type = "Não detectada"

    forensic_details = (
        "Resultado calculado com base em sinais visuais, análise de áudio "
        "e verificação de metadados do arquivo. Cortes de áudio, ausência "
        "de metadados ou recompressão podem indicar edição, mas não confirmam, "
        "isoladamente, uso de inteligência artificial."
    )

    return {
        "confidence_score": confidence_score,
        "classification": "MANIPULADO" if is_deepfake else "REAL",
        "details": {
            "manipulation_type": manipulation_type,
            "audio_sync": audio_result.get("audio_sync", "Não informado"),
            "metadata_flags": metadata_result.get("metadata_flags", []),
            "forensic_details": forensic_details,
            "scores_breakdown": {
                "visual": round(visual_score * 100),
                "audio": round(audio_suspicion * 100),
                "metadata": round(metadata_score * 100),
                "compression": 0,
            },
            "layer_scores": {
                "visual": round(visual_score * 100),
                "audio": round(audio_suspicion * 100),
                "metadata": round(metadata_score * 100),
                "compression": 0,
            },
            "video_info": {
                "filename": filename,
                "sha256": file_hash,
                "frames_analyzed": visual_result.get("frames_analyzed", 0),
                "raw_visual_result": visual_result,
                "raw_audio_result": audio_result,
                "raw_metadata_result": metadata_result,
            },
        },
    }


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    temp_filename = f"{uuid4()}_{file.filename}"
    temp_path = BASE_UPLOAD_DIR / temp_filename

    try:
        with temp_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        validation = validate(str(temp_path), file.filename)

        if not validation["is_valid"]:
            temp_path.unlink(missing_ok=True)

            errors = validation["errors"]
            error_message = errors[0] if errors else "Arquivo inválido."
            error_message_lower = error_message.lower()

            if (
                "extensao" in error_message_lower
                or "extensão" in error_message_lower
                or "invalida" in error_message_lower
                or "inválida" in error_message_lower
            ):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "INVALID_FORMAT",
                            "message": error_message,
                        }
                    },
                )

            if "arquivo muito grande" in error_message_lower:
                raise HTTPException(
                    status_code=413,
                    detail={
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": error_message,
                        }
                    },
                )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_VIDEO",
                        "message": error_message,
                    }
                },
            )

        file_hash = calculate_sha256(str(temp_path))

        cached_analysis = check_cache(file_hash, db)

        if cached_analysis:
            return {
                "task_id": str(cached_analysis.task_id),
                "status": cached_analysis.status,
                "progress": cached_analysis.progress,
                "cached": True,
            }

        task_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        created_at_db = created_at.replace(tzinfo=None)

        analysis_result = build_real_result(
            str(temp_path),
            file_hash,
            file.filename,
        )

        nova_analise = Analise(
            user_id=None,
            task_id=task_id,
            video_hash=file_hash,
            nome_arquivo=file.filename,
            status="completed",
            progress=100,
            criado_em=created_at_db,
            atualizado_em=created_at_db,
        )

        db.add(nova_analise)
        db.flush()

        resultado = ResultadoIA(
            analise_id=nova_analise.id,
            score_confianca=analysis_result["confidence_score"],
            classificacao=analysis_result["classification"],
            detalhes_json=analysis_result["details"],
            finalizado_em=created_at_db,
            criado_em=created_at_db,
            atualizado_em=created_at_db,
        )

        db.add(resultado)
        db.commit()
        db.refresh(nova_analise)

        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "created_at": created_at.isoformat(),
        }

    except HTTPException:
        raise

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "ANALYSIS_ALREADY_EXISTS",
                    "message": str(exc),
                }
            },
        )

    except Exception as exc:
        db.rollback()
        temp_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                }
            },
        )