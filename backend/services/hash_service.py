import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from backend.crud.analise_crud import get_analise_by_hash


CHUNK_SIZE = 8192


def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()

    path = Path(file_path)

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


def check_cache(video_hash: str, db_session: Session):
    return get_analise_by_hash(db_session, video_hash)