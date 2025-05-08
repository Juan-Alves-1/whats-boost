import sys
from celery import Celery
from app.config.settings import settings

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

celery = Celery(
    "whatsboost",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery.conf.update(
    task_track_started=True, # Mark tasks as "STARTED" in the backend 
    worker_hijack_root_logger=False,  # Prevent Celery from overriding logs
)

# Not working properly since celery couldn't find tasks by name
# celery.autodiscover_tasks(packages=["app.tasks"]) 

from app.tasks import batch_queue

celery.conf.task_routes = {
    "app.tasks.batch_queue.enqueue_user_media_batch": {"queue": "scheduler"},
    "app.tasks.batch_queue.send_user_media_batch": {"queue": "media"},
    "app.tasks.batch_queue.send_media_message_subtask": {"queue": "media"},
    "app.tasks.batch_queue.release_and_check_queue": {"queue": "media"},
}

