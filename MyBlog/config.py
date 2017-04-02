import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'Free like a pirate.'
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_MAIL_SUBJECT_PREFIX = '[Patrick]'
    FLASK_MAIL_SENDER = 'Patrick <{}>'.format(os.environ.get('MAIL_USERNAME'))
    FLASK_ADMIN = os.environ.get('MAIL_USERNAME')
    FLASK_POSTS_PER_PAGE = 10
    FLASK_COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevementConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 25  # SSL，TLS都不要开...就是这个端口了
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty.sqlite')


config = {
    'development': DevementConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevementConfig
}
