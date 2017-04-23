#! /usr/bin/env python3

import os
from app import create_app, db
from app.models import Account, Post, UserInfo, Role, ContactMeInfo
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage  # 测量单元测试的覆盖度
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Account=Account, Post=Post, UserInfo=UserInfo, Role=Role, ContactMeInfo=ContactMeInfo)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        # 重启 Python 脚本
        # sys.executable 是 Python 的执行路径
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

if __name__ == '__main__':
    manager.run()
