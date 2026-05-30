import os
import subprocess
from pathlib import Path

# Limites e extensões permitidas
MAX_FILE_SIZE_MB = 500
ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def validate(file_path: str, filename: str) -> dict:
    """
    Executa três camadas de validação em um arquivo de vídeo.
    Retorna um dicionário: {"is_valid": bool, "errors": list[str]}
    """
    errors = []
    is_valid = True

    # 1. Validação de Extensão
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(f"Extensão de arquivo inválida: {ext}. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
        is_valid = False

    # 2. Validação de Tamanho (em bytes)
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            errors.append(f"Arquivo muito grande ({size_mb:.2f} MB). O limite é {MAX_FILE_SIZE_MB} MB.")
            is_valid = False
    except FileNotFoundError:
        errors.append("Arquivo não encontrado para verificação de tamanho.")
        return {"is_valid": False, "errors": errors}

    # Se falhou nas validações básicas, não chama o FFprobe
    if not is_valid:
        return {"is_valid": False, "errors": errors}

    # 3. Validação Profunda com FFprobe (Protegido contra Shell Injection)
    try:
        command = [
            "ffprobe",
            "-v", "error",            
            "-show_format",           
            "-show_streams",          
            file_path
        ]
        
        subprocess.run(command, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        errors.append("O arquivo não é um formato de vídeo válido ou está corrompido.")
        is_valid = False
    except FileNotFoundError:
        errors.append("Erro interno: FFprobe não está instalado ou não foi encontrado no sistema.")
        is_valid = False
    except Exception as e:
        errors.append(f"Erro inesperado ao validar o vídeo: {str(e)}")
        is_valid = False

    return {
        "is_valid": is_valid,
        "errors": errors
    }