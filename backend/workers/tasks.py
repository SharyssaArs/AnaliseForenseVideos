from backend.workers.celery_app import celery_app
from backend.core.database import get_db_context
from backend.crud import update_analise_status


@celery_app.task(bind=True, name="backend.workers.tasks.process_analysis")
def process_analysis(self, task_id: str, file_path: str, analise_id: str):
    """
    Tarefa Celery responsável por processar a análise de vídeo.

    Parâmetros:
        task_id    — UUID da tarefa (usado para rastreamento)
        file_path  — caminho do vídeo salvo em disco
        analise_id — ID do registro na tabela analises
    """
    try:
        with get_db_context() as db:
            update_analise_status(db, analise_id, "processing", 10)

        # TODO: integrar análise real aqui
        # Exemplo futuro:
        #
        # from backend.services.visual_analysis import analyze_video
        # from backend.services.external_apis import get_external_validation
        # from backend.crud import create_resultado_ia
        #
        # score = analyze_video(file_path)
        # external = get_external_validation(file_path, score)
        #
        # with get_db_context() as db:
        #     create_resultado_ia(
        #         db,
        #         analise_id=analise_id,
        #         score_confianca=score,
        #         classificacao="MANIPULADO" if score >= 0.5 else "REAL",
        #         detalhes_json=external,
        #     )
        #     update_analise_status(db, analise_id, "completed", 100)

        with get_db_context() as db:
            update_analise_status(db, analise_id, "completed", 100)

    except Exception as exc:
        with get_db_context() as db:
            update_analise_status(db, analise_id, "failed", 0)
        raise exc
