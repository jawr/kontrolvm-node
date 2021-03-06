from __future__ import absolute_import
from celery import Celery
from celery.utils.log import get_task_logger

celery = Celery('proj.celery',
                broker='amqp://guest@localhost:5672//',
                backend='amqp',
                include=['tasks'])

logger = get_task_logger(__name__)

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    celery.start()
