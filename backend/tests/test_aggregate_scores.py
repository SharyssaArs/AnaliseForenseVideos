from unittest.mock import patch
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from workers.tasks import aggregate_scores, DEEPFAKE_THRESHOLD


def _make_result(score, flags=None):
    return {"score": score, "flags": flags or []}


# Cenario 1: score alto (>0.60) classifica como MANIPULADO sem acionar API
def test_score_alto_classifica_manipulado_sem_api():
    visual = _make_result(0.95)
    audio = _make_result(0.95)
    metadata = _make_result(0.95)

    with patch("workers.tasks.call_reality_defender") as mock_api:
        resultado = aggregate_scores(visual, audio, metadata)

    assert resultado["classificacao"] == "MANIPULADO"
    assert resultado["score_ponderado"] == 0.95
    assert resultado["detalhes_json"]["decisao"] == "score_alto_sem_api"
    mock_api.assert_not_called()


# Cenario 2: score baixo (<0.40) classifica como REAL sem acionar API
def test_score_baixo_classifica_real_sem_api():
    visual = _make_result(0.10)
    audio = _make_result(0.10)
    metadata = _make_result(0.10)

    with patch("workers.tasks.call_reality_defender") as mock_api:
        resultado = aggregate_scores(visual, audio, metadata)

    assert resultado["classificacao"] == "REAL"
    assert resultado["score_ponderado"] == 0.10
    assert resultado["detalhes_json"]["decisao"] == "score_baixo_sem_api"
    mock_api.assert_not_called()


# Cenario 3: score ambiguo (0.52) aciona API e retorna MANIPULADO
def test_score_ambiguo_aciona_api_retorna_manipulado():
    visual = _make_result(0.52)
    audio = _make_result(0.52)
    metadata = _make_result(0.52)

    api_response = {"classificacao": "MANIPULADO", "confianca": 0.87}

    with patch("workers.tasks.call_reality_defender", return_value=api_response) as mock_api:
        resultado = aggregate_scores(visual, audio, metadata)

    assert resultado["classificacao"] == "MANIPULADO"
    assert resultado["detalhes_json"]["decisao"] == "score_ambiguo_api_acionada"
    assert resultado["detalhes_json"]["reality_defender"] == api_response
    mock_api.assert_called_once()


# Cenario 4: score ambiguo aciona API e retorna REAL
def test_score_ambiguo_aciona_api_retorna_real():
    visual = _make_result(0.48)
    audio = _make_result(0.55)
    metadata = _make_result(0.50)

    api_response = {"classificacao": "REAL", "confianca": 0.72}

    with patch("workers.tasks.call_reality_defender", return_value=api_response):
        resultado = aggregate_scores(visual, audio, metadata)

    assert resultado["classificacao"] == "REAL"
    assert resultado["detalhes_json"]["reality_defender"] == api_response


# Cenario 5: API indisponivel ativa fallback com nota em detalhes_json
def test_api_indisponivel_ativa_fallback():
    visual = _make_result(0.52)
    audio = _make_result(0.52)
    metadata = _make_result(0.52)

    with patch("workers.tasks.call_reality_defender", side_effect=Exception("timeout")):
        resultado = aggregate_scores(visual, audio, metadata)

    assert resultado["detalhes_json"]["decisao"] == "fallback_sem_api"
    assert "fallback_nota" in resultado["detalhes_json"]
    assert "indisponivel" in resultado["detalhes_json"]["fallback_nota"].lower() or \
           "timeout" in resultado["detalhes_json"]["fallback_nota"]
    # Classificacao cai no threshold local
    esperado = "MANIPULADO" if resultado["score_ponderado"] > DEEPFAKE_THRESHOLD else "REAL"
    assert resultado["classificacao"] == esperado


# Cenario 6: metadata_flags sem duplicatas
def test_metadata_flags_sem_duplicatas():
    visual = _make_result(0.95, flags=["face_swap", "artifact"])
    audio = _make_result(0.95, flags=["artifact", "audio_gap"])
    metadata = _make_result(0.95, flags=["face_swap", "audio_gap", "timestamp_anomaly"])

    resultado = aggregate_scores(visual, audio, metadata)

    flags = resultado["metadata_flags"]
    assert len(flags) == len(set(flags)), "metadata_flags contem duplicatas"
    assert set(flags) == {"face_swap", "artifact", "audio_gap", "timestamp_anomaly"}
