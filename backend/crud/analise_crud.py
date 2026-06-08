from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.analise import Analise


def create_analise(
    db: Session,
    user_id: str,
    task_id: str,
    video_hash: str,
    nome_arquivo: str,
):
    analise = Analise(
        user_id=user_id,
        task_id=task_id,
        video_hash=video_hash,
        nome_arquivo=nome_arquivo,
        status="pending",
        progress=0,
    )

    db.add(analise)
    db.commit()
    db.refresh(analise)

    return analise


def get_analise_by_hash(
    db: Session,
    video_hash: str,
):
    return (
        db.query(Analise)
        .filter(
            Analise.video_hash == video_hash,
            Analise.status == "completed",
        )
        .order_by(Analise.atualizado_em.desc())
        .first()
    )
# Função pra usar em analyze.py
def get_analise_by_task_id(
    db: Session,
    task_id: str,
):
    return (
        db.query(Analise)
        .filter(Analise.task_id == task_id)
        .first()
    )

# -->
def get_history_by_user(
    db: Session,
    user_id: str,
    page: int,
    limit: int,
):
    offset = (page - 1) * limit

    return (
        db.query(Analise)
        .filter(
            Analise.user_id == user_id
        )
        .order_by(
            Analise.criado_em.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

def update_analise_status(
    db: Session,
    analise_id: str,
    status: str,
    progress: int,
):
    analise = (
        db.query(Analise)
        .filter(Analise.id == analise_id)
        .first()
    )

    if analise is None:
        return None

    analise.status = status
    analise.progress = progress
    analise.atualizado_em = datetime.utcnow()

    db.commit()
    db.refresh(analise)

    return analise