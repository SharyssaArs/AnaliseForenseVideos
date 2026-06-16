import os
import traceback
from datetime import datetime
from decimal import Decimal

from celery import shared_task

from backend.core.database import SessionLocal
from backend.models.analise import Analise
from backend.models.log_processamento import LogProcessamento
from backend.models.resultado_ia import ResultadoIA
from backend.services import audio_analysis, external_apis, metadata_analysis, visual_analysis


def atualizar_analise(db, analise, status=None, progress=None):
    if status is not None:
        analise.status = status

    if progress is not None:
        analise.progress = progress

    analise.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(analise)


def registrar_log(db, analise_id, etapa, status, mensagem):
    log = LogProcessamento(
        analise_id=analise_id,
        etapa=etapa,
        status=status,
        mensagem=mensagem,
    )

    db.add(log)
    db.commit()

    return log


def extrair_score(resultado):
    if isinstance(resultado, dict):
        for chave in ("score", "score_confianca", "confidence"):
            if chave in resultado and resultado[chave] is not None:
                return float(resultado[chave])

    return 0.0


def aggregate_scores(visual_result, audio_result, metadata_result, external_result=None):
    resultados = [visual_result, audio_result, metadata_result]

    if external_result is not None:
        resultados.append(external_result)

    scores = [extrair_score(resultado) for resultado in resultados]
    score_final = sum(scores) / len(scores) if scores else 0.0

    classificacao = "MANIPULADO" if score_final >= 0.5 else "REAL"

    return {
        "score": score_final,
        "classificacao": classificacao,
        "detalhes": {
            "visual_analysis": visual_result,
            "audio_analysis": audio_result,
            "metadata_analysis": metadata_result,
            "external_apis": external_result,
        },
    }


def score_ambiguo(score):
    return 0.45 <= float(score) <= 0.55


@shared_task(name="process_video_task")
def process_video_task(task_id, file_path, video_hash):
    db = SessionLocal()
    analise = None

    try:
        analise = db.query(Analise).filter(Analise.task_id == task_id).first()

        if analise is None:
            raise ValueError(f"Análise não encontrada para task_id: {task_id}")

        atualizar_analise(db, analise, status="processing", progress=10)

        registrar_log(db, analise.id, "visual_analysis", "iniciado", "Iniciando análise visual.")
        visual_result = visual_analysis.analyze(file_path)
        registrar_log(db, analise.id, "visual_analysis", "sucesso", "Análise visual concluída.")
        atualizar_analise(db, analise, progress=40)

        registrar_log(db, analise.id, "audio_analysis", "iniciado", "Iniciando análise de áudio.")
        audio_result = audio_analysis.analyze(file_path)
        registrar_log(db, analise.id, "audio_analysis", "sucesso", "Análise de áudio concluída.")
        atualizar_analise(db, analise, progress=65)

        registrar_log(db, analise.id, "metadata_analysis", "iniciado", "Iniciando análise de metadados.")
        metadata_result = metadata_analysis.analyze(file_path)
        registrar_log(db, analise.id, "metadata_analysis", "sucesso", "Análise de metadados concluída.")
        atualizar_analise(db, analise, progress=80)

        external_result = None

        resultado_agregado = aggregate_scores(
            visual_result,
            audio_result,
            metadata_result,
        )

        if score_ambiguo(resultado_agregado["score"]):
            registrar_log(
                db,
                analise.id,
                "external_apis",
                "iniciado",
                "Score ambíguo. Consultando APIs externas.",
            )

            external_result = external_apis.analyze(file_path, video_hash)

            registrar_log(
                db,
                analise.id,
                "external_apis",
                "sucesso",
                "Consulta em APIs externas concluída.",
            )

            resultado_agregado = aggregate_scores(
                visual_result,
                audio_result,
                metadata_result,
                external_result,
            )

        atualizar_analise(db, analise, progress=95)

        resultado_ia = ResultadoIA(
            analise_id=analise.id,
            score_confianca=Decimal(str(round(float(resultado_agregado["score"]), 4))),
            classificacao=resultado_agregado["classificacao"],
            detalhes_json=resultado_agregado["detalhes"],
            finalizado_em=datetime.utcnow(),
        )

        db.add(resultado_ia)
        db.commit()

        registrar_log(
            db,
            analise.id,
            "resultado_ia",
            "sucesso",
            "Resultado final salvo na tabela resultados_ia.",
        )

        atualizar_analise(db, analise, status="completed", progress=100)

        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "score": float(resultado_agregado["score"]),
            "classificacao": resultado_agregado["classificacao"],
        }

    except Exception as erro:
        db.rollback()

        mensagem_erro = str(erro)
        detalhes_erro = traceback.format_exc()

        if analise is None:
            analise = db.query(Analise).filter(Analise.task_id == task_id).first()

        if analise is not None:
            analise.status = "failed"
            analise.atualizado_em = datetime.utcnow()
            db.commit()

            registrar_log(
                db,
                analise.id,
                "erro_processamento",
                "erro",
                f"{mensagem_erro}\n\n{detalhes_erro}",
            )

        return {
            "task_id": task_id,
            "status": "failed",
            "error": mensagem_erro,
        }

    finally:
        db.close()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)
