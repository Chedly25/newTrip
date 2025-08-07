from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "wanderlog_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.tasks']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.workers.tasks.*': {'queue': 'default'},
    }
)