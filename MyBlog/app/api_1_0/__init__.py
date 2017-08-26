"""
- 创建 API 蓝图
- 编写处理错误的函数，返回 json
- 编写认证，要用 HTTPBasicAuth 初始一个实例，然后就可以用类似于 flask_login 里面的 login_required 了
- 把资源 json 化
- 实现请求端点，返回 json
"""

from flask import Blueprint

api = Blueprint('api', '__name__')

from . import errors, authentication, decorators, posts, users
