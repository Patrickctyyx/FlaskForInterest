import os
import datetime
from celery.schedules import crontab
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '9bf73061cbfa3acc637aae5b506bebde'
    pc_id = 'c70916fe0d1533db47fbc6b28fa60519'
    pc_key = '791f706df9dbaf6e0f0fe7df1f413b58'


class ProdConfig(Config): 
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    SQLALCHEMT_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MONGODB_SETTINGS = {
        'db': 'local',
        'host': 'localhost',
        'port': 27017
    }
    CELERY_BROKER_URL = "redis://localhost:6379"
    # 配置名不能错，不然就注册不了相应的配置
    # 我在这个地方就卡了很久！
    CELERY_RESULT_BACKEND = "redis://localhost:6379"
    CELERYBEAT_SCHEDULE = {
        'week-digest': {
            'task': 'task.digest',
            'schedule': crontab(day_of_week=6, hour='10')
        },
        'log-every-5-seconds': {
            'task': 'webapp.tasks.log',
            'schedule': crontab(minute='*/1'),
            'args': ['patrick', ]
        },
    }

config = {
    'dev': DevConfig
}

