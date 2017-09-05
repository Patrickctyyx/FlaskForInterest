from flask import Blueprint, render_template, Markup


class Youtube:
    def __init__(self, app=None, **kwargs):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.register_blueprint(app)
        app.add_template_global(youtube)

    def register_blueprint(self, app):
        module = Blueprint(
            'youtube',
            __name__,
            template_folder='templates'
        )
        app.register_blueprint(module)
        return module


class Video:
    def __init__(self, video_id, cls='youtube'):
        self.video_id = video_id
        self.cls = cls

    def render(self, *args, **kwargs):
        return render_template(*args, **kwargs)

    @property
    def html(self):
        return Markup(
            self.render('youtube/video.html', video=self)
        )


def youtube(*args, **kwargs):
    video = Video(*args, **kwargs)
    return video.html