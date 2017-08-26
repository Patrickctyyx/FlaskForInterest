from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed
from flask_restful import Api
from flask_celery import Celery

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


@login_manger.user_loader
def load_user(userid):
    from .models import User
    return User.query.get(userid)
