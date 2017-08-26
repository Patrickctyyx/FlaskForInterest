from webapp.extensions import celery


@celery.task
def log(msg):
    return msg
