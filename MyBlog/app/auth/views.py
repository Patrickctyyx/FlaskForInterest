from . import auth
from .. import db
import hashlib
from ..models import Account, UserInfo, Verify, Role
from ..emails import send_email
from .forms import LoginForm, RegisterForm, ChangePassForm, VerifyEmailForm, ResetPassForm
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误。')
    return render_template('auth/login.html', form=form)  # 路径是相对templates的


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经成功登出。')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Account(password=form.password.data,
                       email=form.email.data,
                       username=form.username.data,
                       phone=form.phone.data)
        if form.email.data == current_app.config['FLASK_ADMIN']:
            role = Role.query.filter_by(permissions=0xff).first()
            user.role = role
        db.session.add(user)
        db.session.flush()
        userinfo = UserInfo()
        userinfo.uid = user.uid
        db.session.add(userinfo)
        db.session.commit()
        login_user(user, False)
        token = user.generate_confirmation_token()
        send_email(user.email, '确认你的邮件',
                   'auth/email/confirm', user=user, token=token)
        flash('一封确认邮箱的邮件已经发送到了你的邮箱中，请注意查收！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你的账户已经成功确认！')
    else:
        flash('确认链接已经失效！')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            # 请求静态文件也不拦截
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('确认邮件已经发送到了你的邮箱，请注意查收！')
    return redirect(url_for('main.index'))


# @auth.route('/changepasswd', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     form = ChangePassForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.former_pass.data):
#             current_user.password = form.password.data
#             db.session.add(current_user)
#             db.session.commit()
#             flash('成功更改密码！')
#             return redirect(url_for('main.index'))
#         flash('请输入正确的密码！')
#     return render_template('auth/password.html', form=form)
#
#
# @auth.route('/forgetpasswd', methods=['GET', 'POST'])
# def forget_password():  # 发送验证邮件
#     form = VerifyEmailForm()
#     if form.validate_on_submit():
#         verify = Verify(form.email.data)
#         token = verify.generate_confirmation_token()
#         send_email(form.email.data, 'Verify Your Email',
#                    'auth/email/verify', token=token, email=form.email.data)
#         flash('一封确认邮件已经发送到了你的邮箱。如果你没有收到有钱，氢回到上一页重新发送。')
#         return redirect(url_for('main.index'))
#     return render_template('auth/submit_email.html', form=form)
#
#
# @auth.route('/resetpasswd/<token>/<email>', methods=['GET', 'POST'])
# def reset_password(token, email):
#     verify = Verify(email)
#     userinfo = UserInfo.query.filter_by(email=email).first()
#     if not userinfo:
#         flash('The email is invalid!')
#         return redirect(url_for('auth.forget_password'))
#     if verify.confirm(token):
#         flash('You have verified your account. And you can reset your password now!')
#         form = ResetPassForm()
#         if form.validate_on_submit():
#             user = Account.query.get(userinfo.uid)
#             user.password = form.password.data  # 修改密码要这样，其中user.password并不是数据库对应的密码字段
#             login_user(user, False)
#             db.session.add(user)
#             db.session.commit()
#             flash('成功重置密码！')
#             return redirect(url_for('main.index'))
#         return render_template('auth/reset_pass.html', form=form)
#     else:
#         flash('The confirmation link is invalid or has expired.')
#         return redirect(url_for('main.index'))
#
#
# @auth.route('/changemail', methods=['GET', 'POST'])
# @login_required
# def check_mail():  # 发送验证邮件
#     form = VerifyEmailForm()
#     if form.validate_on_submit():
#         token = current_user.generate_confirmation_token()
#         email = form.email.data
#         send_email(email, 'Verify Your Email',
#                    'auth/email/verify_mail', token=token, email=email)
#         flash('A verification email has been sent to your email. If you didn\'t receive the email,'
#               ' go back to the previous page and check your email.')
#         return redirect(url_for('main.index'))
#     return render_template('auth/reset_mail.html', form=form)
#
#
# @auth.route('/changemail/<token>/<email>', methods=['GET', 'POST'])
# @login_required
# def change_mail(token, email):
#     if current_user.confirm(token):
#         flash('You have verified your account. And you can change your email now!')
#         userinfo = UserInfo.query.filter_by(uid=current_user.uid).first()
#         userinfo.email = email
#         userinfo.avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
#         db.session.add(userinfo)
#         db.session.commit()
#         flash('成功修改邮箱！')
#         return redirect(url_for('main.index'))
#     else:
#         flash('The confirmation link is invalid or has expired.')
#         return redirect(url_for('main.index'))

