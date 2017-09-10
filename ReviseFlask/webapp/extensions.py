from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed
from flask_restful import Api
from flask_celery import Celery
from flask_debugtoolbar import DebugToolbarExtension
from flask_cache import Cache
from flask import request
from gzip import GzipFile
from io import BytesIO


bcrypt = Bcrypt()

login_manger = LoginManager()
login_manger.login_view = 'main.login'
login_manger.session_protection = 'strong'
login_manger.login_message = '请登录以访问该页面'
login_manger.login_message_category = 'info'

principals = Principal()
admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))

rest_api = Api()

celery = Celery()

debug_toolbar = DebugToolbarExtension()

cache = Cache()


@login_manger.user_loader
def load_user(userid):
    from .models import User
    return User.query.get(userid)


class GZip:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.after_request(self.after_request)

    def after_request(self, response):
        encoding = request.headers.get('Accept-Encoding', '')

        if 'gzip' not in encoding or response.status_code not in (200, 201):
            return response

        response.direct_passthrough = False

        contents = BytesIO()
        with GzipFile(
            mode='wb',
            compresslevel=5,
            fileobj=contents
        ) as gzip_file:
            gzip_file.write(response.get_data())

        response.set_data(bytes(contents.getvalue()))
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = response.content_length

        return response

flask_gzip = GZip()



