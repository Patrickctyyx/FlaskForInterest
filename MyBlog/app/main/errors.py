from flask import render_template
from . import main


@main.app_errorhandler(404)  # 蓝图的错误处理和普通的不同，要用这个才能被全局触发
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
