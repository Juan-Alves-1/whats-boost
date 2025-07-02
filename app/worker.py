from celery import Celery

from app.config.settings import settings

celery = Celery(
    "whatsboost",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery.conf.update(
    task_track_started=True, # Mark tasks as "STARTED" in the backend 
    worker_hijack_root_logger=False,  # Prevent Celery from overriding logs
)

celery.autodiscover_tasks(packages=["app.tasks"]) 
