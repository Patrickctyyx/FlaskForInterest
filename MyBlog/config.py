import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'Free like a pirate.'

    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    FLASK_SLOW_DB_QUERY_TIME = 0.5

    FLASK_MAIL_SUBJECT_PREFIX = '[Patrick]'
    FLASK_MAIL_SENDER = 'Patrick <{}>'.format(os.environ.get('MAIL_USERNAME'))
    FLASK_ADMIN = os.environ.get('MAIL_USERNAME')
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 25  # SSL，TLS都不要开...就是这个端口了
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    FLASK_POSTS_PER_PAGE = 10
    FLASK_COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevementConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cty.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            mail_handler = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr=cls.FLASK_MAIL_SENDER,
                toaddrs=['873948000@qq.com'],
                subject=cls.FLASK_MAIL_SUBJECT_PREFIX + 'Application Error',
                credentials=credentials,
                secure=None
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


class UnixConfig(Config):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)  # 日志会被写到 /vae/log/messages


config = {
    'development': DevementConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,
    'default': DevementConfig
}
