from flask import Flask, redirect, url_for
from .config import config
from .models import db
from .extensions import bcrypt
from .controllers.blog import blog_print
from .controllers.main import main_blueprint


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(config[object_name])

    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(blog_print)
    app.register_blueprint(main_blueprint)

    return app


