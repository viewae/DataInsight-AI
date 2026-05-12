from celery_app import celery_app


@celery_app.task(name="datainsight.ping")
def ping() -> str:
    return "pong"
