import os
from flask import Flask
from .config import config
from .models import db, Role, Reminder, User, Post, Comment, Tag, Contact
from .extensions import bcrypt, login_manger, principals, rest_api, celery, debug_toolbar, cache, admin
from .controllers.blog import blog_print
from .controllers.main import main_blueprint
from .controllers.admin import CustomView, CustomModelView, CustomFileAdmin
from .controllers.rest.post import PostApi
from .controllers.rest.auth import AuthApi
from .controllers.rest.contact import ContactApi
from .controllers.rest.comment import CommentApi
from .tasks import on_reminder_save
from sqlalchemy import event
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(config[object_name])

    db.init_app(app)
    event.listen(Reminder, 'after_insert', on_reminder_save)
    bcrypt.init_app(app)
    login_manger.init_app(app)
    principals.init_app(app)
    # mongo.init_app(app)
    celery.init_app(app)  # 使用的扩展不要忘了 init
    rest_api.add_resource(
        PostApi,
        '/api/post',
        '/api/post/<int:post_id>'
    )
    rest_api.add_resource(
        AuthApi,
        '/api/auth'
    )
    rest_api.add_resource(
        CommentApi,
        '/api/comments',
        '/api/post/<int:post_id>/comments'
    )
    rest_api.add_resource(
        ContactApi,
        '/api/contact'
    )
    rest_api.init_app(app)
    debug_toolbar.init_app(app)
    cache.init_app(app)
    admin.init_app(app)
    admin.add_view(CustomView(name='Custom'))
    admin.add_view(CustomFileAdmin(
        os.path.join(os.path.dirname(__file__), 'static'),
        '/static/',
        name='Static Files'
    ))
    models = [User, Reminder, Post, Role, Comment, Contact, Tag]

    for model in models:
        admin.add_view(CustomModelView(model, db.session, category='Models'))

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


