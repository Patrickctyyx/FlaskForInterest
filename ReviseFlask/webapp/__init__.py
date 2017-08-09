from flask import Flask
from .config import config
from .models import db, mongo, Role
from .extensions import bcrypt, login_manger, principals
from .controllers.blog import blog_print
from .controllers.main import main_blueprint
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(config[object_name])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manger.init_app(app)
    principals.init_app(app)
    mongo.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    app.register_blueprint(blog_print)
    app.register_blueprint(main_blueprint)

    return app


