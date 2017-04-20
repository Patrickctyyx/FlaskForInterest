"""由于 REST Web 服务的一个特征是无状态，因此用 cookie 保存会话是不现实的，这里使用 HTTP 认证"""


from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from . import api
from .errors import unauthorized, forbidden
from ..models import AnonymousUser, UserInfo, Account
auth = HTTPBasicAuth()  # 只在蓝图中使用，不必在程序包中初始化


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = Account.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    userinfo = UserInfo.query.filter_by(email=email_or_token).first()
    if not userinfo:
        return False
    account = Account.query.get(userinfo.uid)
    g.current_user = account
    g.token_used = False
    return account.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonoymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonoymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
