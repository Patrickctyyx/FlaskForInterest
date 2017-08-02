import os
basedir = os.path.abspath(os.path.pardir)


class Config:
    SECRET_KEY = '9bf73061cbfa3acc637aae5b506bebde'


class ProdConfig(Config): 
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.pardir, 'dev.sqlite')
    SQLALCHEMT_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

config = {
    'dev': DevConfig
}
