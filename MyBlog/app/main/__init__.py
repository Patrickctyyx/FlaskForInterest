from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)  # 参数为蓝图的名字和所在的包或模块


@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)

from . import views, errors  # 避免循环导入
