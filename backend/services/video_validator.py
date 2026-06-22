import os
import subprocess
from pathlib import Path

import magic

MAX_FILE_SIZE_MB = 500
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}


def validate(file_path: str, filename: str) -> dict:
    errors = []
    is_valid = True

    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        errors.append(
            f"Extensão inválida: {ext}. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        is_valid = False

    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            errors.append(
                f"Arquivo muito grande ({size_mb:.2f} MB). Limite: {MAX_FILE_SIZE_MB} MB."
            )
            is_valid = False

    except FileNotFoundError:
        errors.append("Arquivo não encontrado.")
        return {"is_valid": False, "errors": errors}

    if not is_valid:
        return {"is_valid": False, "errors": errors}

    try:
        mime_type = magic.from_file(file_path, mime=True)

        if mime_type not in ALLOWED_MIME_TYPES:
            errors.append(f"Tipo MIME inválido: {mime_type}.")
            is_valid = False

    except Exception as error:
        errors.append(f"Erro ao validar MIME type: {str(error)}")
        is_valid = False

    if not is_valid:
        return {"is_valid": False, "errors": errors}

    try:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            file_path,
        ]

        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError:
        errors.append("O arquivo não é um vídeo válido ou está corrompido.")
        is_valid = False

    except FileNotFoundError:
        errors.append("FFprobe não está instalado ou não foi encontrado.")
        is_valid = False

    except Exception as error:
        errors.append(f"Erro inesperado ao validar vídeo: {str(error)}")
        is_valid = False

    return {
        "is_valid": is_valid,
        "errors": errors,
    }