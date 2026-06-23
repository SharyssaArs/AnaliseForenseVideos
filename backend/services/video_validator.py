import os
import subprocess
from pathlib import Path


MAX_FILE_SIZE_MB = 500
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}


def detect_mime_type(file_path: str) -> tuple[str | None, str | None]:
    """
    Usa python-magic quando a libmagic nativa estiver instalada.
    No Windows local, a DLL pode faltar; nesse caso o backend deve continuar subindo.
    """
    try:
        import magic

        return magic.from_file(file_path, mime=True), None
    except Exception as error:
        return None, str(error)


def validate(file_path: str, filename: str) -> dict:
    errors = []
    warnings = []
    is_valid = True

    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        errors.append(
            f"Extensao invalida: {ext}. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
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
        errors.append("Arquivo nao encontrado.")
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    if not is_valid:
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    mime_type, mime_error = detect_mime_type(file_path)

    if mime_type is None:
        warnings.append(
            "Validacao MIME ignorada porque python-magic/libmagic nao esta disponivel: "
            f"{mime_error}"
        )
    elif mime_type not in ALLOWED_MIME_TYPES:
        errors.append(f"Tipo MIME invalido: {mime_type}.")
        is_valid = False

    if not is_valid:
        return {"is_valid": False, "errors": errors, "warnings": warnings}

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
        errors.append("O arquivo nao e um video valido ou esta corrompido.")
        is_valid = False

    except FileNotFoundError:
        warnings.append("FFprobe nao esta instalado ou nao foi encontrado.")

    except Exception as error:
        errors.append(f"Erro inesperado ao validar video: {str(error)}")
        is_valid = False

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
    }
