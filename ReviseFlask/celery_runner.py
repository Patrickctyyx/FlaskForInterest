from webapp import create_app
# from celery import Celery
from webapp.tasks import log  # 这个不能省，不然在运行 celery 的时候会报错
from webapp.extensions import celery  # 如果使用 flask-celery 就不用下面的函数了


# def make_celery(app):
#     celery = Celery(
#         app.import_name,
#         backend=app.config['CELERY_RESULT_BACKEND'],
#         broker=app.config['CELERY_BROKER_URL']
#     )
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#
#     class ContextTask(TaskBase):
#         abstract = True
#
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#
#     celery.Task = ContextTask
#
#     return celery

flask_app = create_app('dev')

# celery = make_celery(flask_app)
