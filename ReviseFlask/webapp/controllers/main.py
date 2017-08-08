from flask import Blueprint, redirect, url_for, render_template, session, request, flash, current_app
from webapp.forms import LoginForm, RegisterForm
from webapp.config import Config
from webapp.sdk import GeetestLib
from webapp.models import db, User
from .blog import sidebar_data
from flask_login import login_user, logout_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


@main_blueprint.app_errorhandler(404)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('404.html', recent=recent, top_tags=top_tags), 404


@main_blueprint.app_errorhandler(403)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('403.html', recent=recent, top_tags=top_tags), 403


@main_blueprint.app_errorhandler(500)
def page_not_found(error):
    recent, top_tags = sidebar_data()
    return render_template('500.html', recent=recent, top_tags=top_tags), 500


@main_blueprint.route('/')
def index():
    return redirect(url_for('blog.home'))


@main_blueprint.route('/pc-geetest/register', methods=['GET'])
def get_pc_captcha():
    gt = GeetestLib(Config.pc_id, Config.pc_key)
    status = gt.pre_process()
    session[gt.GT_STATUS_SESSION_KEY] = status
    response_str = gt.get_response_str()
    return response_str


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        gt = GeetestLib(Config.pc_id, Config.pc_key)
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        if status:
            result = gt.success_validate(challenge, validate, seccode)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user = User.query.filter_by(username=form.username.data).first()
            login_user(user, remember=form.remember_me.data)
            identity_changed.send(
                current_app._get_current_object(),
                identity=Identity(user.id)
            )
            flash('登陆成功！', category='success')
            return redirect(url_for('blog.home'))
        else:
            flash('登录失败')
    return render_template('login.html', form=form)


@main_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    identity_changed.send(  # 改变身份
        current_app._get_current_object(),
        identity=AnonymousIdentity()  # 并触发 on_identity_loaded 函数
    )
    flash('登出成功！', category='success')
    return redirect(url_for('blog.home'))


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(form.username.data)
        user.passwd = form.password.data

        db.session.add(user)
        db.session.commit()

        flash('注册成功！', category='success')
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)
