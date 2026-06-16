from celery import Celery

from backend.core.config import settings

app = Celery(
    "forensic_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

app.conf.update(

    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    timezone="America/Sao_Paulo",
    enable_utc=False,


    result_expires=86400,

   
    task_default_retry_delay=60,

    task_annotations={
        "*": {
            "max_retries": 3,
        }
    },

    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,

    task_routes={
        "backend.workers.tasks.*": {
            "queue": "analysis_queue",
        }
    },

    # Descoberta automática das tasks
    include=[
        "backend.workers.tasks",
    ],
)
