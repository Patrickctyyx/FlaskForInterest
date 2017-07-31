import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    pass


class ProdConfig(Config): 
    pass


class DevConfig(Config):
    debug = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    SQLALCHEMT_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
