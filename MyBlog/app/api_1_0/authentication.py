from flask_httpauth import HTTPBasicAuth
from flask import g
from . import api
from .errors import unauthorized, forbidden
from ..models import AnonymousUser, UserInfo, Account
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True
    userinfo = UserInfo.query.filter_by(email=email).first()
    if not userinfo:
        return False
    account = Account.query.get(userinfo.uid)
    g.current_user = account
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
