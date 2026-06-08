import re

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.database import get_db
from backend.crud.analise_crud import get_analise_by_hash
from backend.api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/cache",
    tags=["Cache"]
)

SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

@router.get("/{hash}")
def verificar_cache(
    hash: str,
    current_user=Depends(get_current_user)
):
    if not SHA256_REGEX.fullmatch(hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de hash inválido. O hash SHA-256 deve conter exatamente 64 caracteres hexadecimais."
        )
    
    with get_db() as db:
        analise = get_analise_by_hash(db, hash)

    if analise is None:
        return{"exists": False}
    
    return{
        "exists": True,
        "task_id": analise.task_id
    }
