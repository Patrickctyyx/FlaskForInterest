from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from main import app, db, User, Post, Tag

migrate = Migrate(app, db)
manger = Manager(app)
manger.add_command('server', Server())
manger.add_command('db', MigrateCommand)


@manger.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Tag=Tag)

if __name__ == '__main__':
    manger.run()
