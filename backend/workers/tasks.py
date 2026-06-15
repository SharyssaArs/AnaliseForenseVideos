from backend.workers.celery_app import app


@app.task(bind=True)
def test_task(self, message: str):

    return {
        "status": "success",
        "message": message,
    }
