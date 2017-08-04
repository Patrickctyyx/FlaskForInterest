from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed

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


@login_manger.user_loader
def load_user(userif):
    from .models import User
    return User.query.get(id)
