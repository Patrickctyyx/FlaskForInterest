import os
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

config = {
    'dev': DevConfig
}

