import logging
import time

import requests

from backend.core.config import settings


AMBIGUOUS_SCORE_MIN = 0.40
AMBIGUOUS_SCORE_MAX = 0.60

logger = logging.getLogger(__name__)

def normalize_score(
    score: float | int | None,
):
    if score is None:
        return None

    score = float(score)

    if score > 1:
        score = score / 100

    return max(
        0.0,
        min(score, 1.0),
    )

def should_call_external_api(
    local_score: float,
):
    return (
        AMBIGUOUS_SCORE_MIN
        <= local_score
        <= AMBIGUOUS_SCORE_MAX
    )

def execute_with_retry(
    request_function,
):
    delays = [1, 2, 4]

    for attempt, delay in enumerate(
        delays,
        start=1,
    ):
        try:

            return request_function()

        except requests.Timeout:

            logger.warning(
                f"Timeout na tentativa "
                f"{attempt}"
            )

        except requests.RequestException as exc:

            status_code = getattr(
                exc.response,
                "status_code",
                None,
            )

            if status_code == 503:

                logger.warning(
                    f"Erro 503 na tentativa "
                    f"{attempt}"
                )

            else:

                logger.warning(
                    f"Falha na tentativa "
                    f"{attempt}: {exc}"
                )

        time.sleep(delay)

    return None

def build_reality_headers():
    return {
        "Authorization":
            f"Bearer "
            f"{settings.REALITY_DEFENDER_API_KEY}"
    }

def submit_to_reality_defender(
    video_path: str,
):
    headers = build_reality_headers()

    with open(video_path, "rb") as video:

        response = requests.post(
            f"{REALITY_DEFENDER_URL}/analyze",
            headers=headers,
            files={
                "file": video
            },
            timeout=30,
        )

    response.raise_for_status()

    return response.json()

def poll_reality_defender(
    job_id: str,
):
    headers = build_reality_headers()

    response = requests.get(
        f"{REALITY_DEFENDER_URL}"
        f"/results/{job_id}",
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def get_reality_defender_score(
    video_path: str,
):
    def request_function():

        upload = (
            submit_to_reality_defender(
                video_path
            )
        )

        job_id = upload.get("job_id")

        if not job_id:
            return None

        result = (
            poll_reality_defender(
                job_id
            )
        )

        score = result.get("score")

        return normalize_score(
            score
        )

    return execute_with_retry(
        request_function
    )

def get_sensity_score(
    video_path: str,
):
    logger.warning(
        "Cliente Sensity ainda "
        "não configurado."
    )

    return None

def get_external_validation(
    video_path: str,
    local_score: float,
):
    if not should_call_external_api(
        local_score
    ):
        return None

    reality_score = (
        get_reality_defender_score(
            video_path
        )
    )

    sensity_score = (
        get_sensity_score(
            video_path
        )
    )

    return {
        "reality_defender":
            reality_score,

        "sensity":
            sensity_score,
    }