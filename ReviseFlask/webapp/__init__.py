from flask import Flask, redirect, url_for
from .config import config
from .models import db
from .controllers.blog import blog_print


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(config[object_name])

    db.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('blog.home'))

    app.register_blueprint(blog_print)

    return app


