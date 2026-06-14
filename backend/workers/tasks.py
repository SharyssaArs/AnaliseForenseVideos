import logging

logger = logging.getLogger(__name__)

DEEPFAKE_THRESHOLD = 0.50
HIGH_CONFIDENCE_THRESHOLD = 0.60
LOW_CONFIDENCE_THRESHOLD = 0.40

try:
    from services.external_apis import call_reality_defender
except (ImportError, AttributeError):
    call_reality_defender = None


def aggregate_scores(visual_result, audio_result, metadata_result):
    visual_score = visual_result.get("score", 0.0)
    audio_score = audio_result.get("score", 0.0)
    metadata_score = metadata_result.get("score", 0.0)

    weighted_score = (
        visual_score * 0.60
        + audio_score * 0.25
        + metadata_score * 0.15
    )

    all_flags = (
        visual_result.get("flags", [])
        + audio_result.get("flags", [])
        + metadata_result.get("flags", [])
    )
    metadata_flags = list(dict.fromkeys(all_flags))

    detalhes_json = {
        "scores": {
            "visual": visual_score,
            "audio": audio_score,
            "metadata": metadata_score,
        },
        "weighted_score": round(weighted_score, 4),
        "pesos": {"visual": 0.60, "audio": 0.25, "metadata": 0.15},
    }

    if weighted_score > HIGH_CONFIDENCE_THRESHOLD:
        classificacao = "MANIPULADO"
        detalhes_json["decisao"] = "score_alto_sem_api"
    elif weighted_score < LOW_CONFIDENCE_THRESHOLD:
        classificacao = "REAL"
        detalhes_json["decisao"] = "score_baixo_sem_api"
    else:
        classificacao = _resolve_ambiguous(weighted_score, detalhes_json)

    return {
        "classificacao": classificacao,
        "score_ponderado": round(weighted_score, 4),
        "metadata_flags": metadata_flags,
        "detalhes_json": detalhes_json,
    }


def _resolve_ambiguous(weighted_score, detalhes_json):
    detalhes_json["decisao"] = "score_ambiguo_api_acionada"

    if call_reality_defender is None:
        return _fallback_classification(
            weighted_score, detalhes_json, motivo="servico_nao_implementado"
        )

    try:
        api_result = call_reality_defender(weighted_score)
        detalhes_json["reality_defender"] = api_result
        return api_result.get("classificacao", _threshold_classify(weighted_score))
    except Exception as exc:
        logger.warning("Reality Defender indisponivel: %s", exc)
        return _fallback_classification(weighted_score, detalhes_json, motivo=str(exc))


def _fallback_classification(weighted_score, detalhes_json, motivo="indisponivel"):
    detalhes_json["decisao"] = "fallback_sem_api"
    detalhes_json["fallback_nota"] = (
        f"API Reality Defender indisponivel ({motivo}). "
        f"Classificacao baseada no threshold local ({DEEPFAKE_THRESHOLD})."
    )
    return _threshold_classify(weighted_score)


def _threshold_classify(score):
    return "MANIPULADO" if score > DEEPFAKE_THRESHOLD else "REAL"
