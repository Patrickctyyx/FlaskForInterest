from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from webapp import create_app
from webapp.models import db, User, Post, Tag, Comment, Role
from fake_posts import generate_fake_posts, init_roles

app = create_app('dev')
migrate = Migrate(app, db)
manger = Manager(app)
manger.add_command('server', Server)
manger.add_command('db', MigrateCommand)
manger.add_command('show', ShowUrls)
manger.add_command('clean', Clean)


@manger.command
def setup():
    init_roles()
    generate_fake_posts()


@manger.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Tag=Tag, Comment=Comment, Role=Role)


if __name__ == '__main__':
    manger.run()
