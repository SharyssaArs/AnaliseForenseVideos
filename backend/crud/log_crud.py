from sqlalchemy.orm import Session

from backend.models.log_processamento import LogProcessamento


def create_log_processamento(
    db: Session,
    analise_id: str,
    etapa: str,
    status: str,
    mensagem: str | None = None,
):
    log = LogProcessamento(
        analise_id=analise_id,
        etapa=etapa,
        status=status,
        mensagem=mensagem,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_logs_by_analise_id(
    db: Session,
    analise_id: str,
):
    return (
        db.query(LogProcessamento)
        .filter(LogProcessamento.analise_id == analise_id)
        .all()
    )