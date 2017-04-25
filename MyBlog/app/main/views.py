from flask import render_template, redirect, url_for, flash, abort, request, current_app

from . import main
from .forms import ContactMeForm, CompleteProfileField, EditProfileField, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import ContactMeInfo, UserInfo, Account, Role, Permission, Post, Comment
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import get_debug_queries


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ContactMeForm()
    form2 = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form2.validate_on_submit():
        post = Post(body=form2.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    if form.validate_on_submit():
        info = ContactMeInfo.query.filter_by(phone=form.phone.data).first()
        if info is None:
            info = ContactMeInfo(name=form.name.data,
                                 phone=form.phone.data,
                                 email=form.email.data,
                                 comment=form.comment.data if form.comment.data else None)
            db.session.add(info)
            db.session.commit()
        else:
            flash('您已经提交过个人信息。')
        return redirect(url_for('.index'))  # 这里的.前面是命名空间，相当于main.index，表示是main这个蓝图下的
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.cred_at.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('home.html', form=form, form2=form2, posts=posts, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = UserInfo.query.filter_by(name=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Account.query.get(user.uid).posts.order_by(Post.cred_at.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    # posts = Account.query.get(user.uid).posts.order_by(Post.cred_at.desc()).all()
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    form = CompleteProfileField()
    userinfo = current_user.userinfo
    if form.validate_on_submit():
        userinfo.phone = form.phone.data
        userinfo.student_id = form.student_id.data
        userinfo.grade = form.grade.data
        userinfo.department = form.department.data
        userinfo.school = form.school.data
        userinfo.major = form.major.data
        userinfo.qq = form.qq.data
        userinfo.introduction = form.introduction.data
        try:
            db.session.add(userinfo)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(str(e.orig).split('.')[1].capitalize() + ' is already existed!')
            return redirect(url_for('.user', username=userinfo.name))
        flash('初始化完成')
        return redirect(url_for('.user', username=userinfo.name))
    form.phone.data = userinfo.phone
    form.student_id.data = userinfo.student_id
    form.grade.data = userinfo.grade
    form.department.data = userinfo.department
    form.school.data = userinfo.school
    form.major.data = userinfo.qq
    form.qq.data = userinfo.qq
    form.introduction.data = userinfo.introduction
    return render_template('complete_profile.html', form=form)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileField()
    userinfo = current_user.userinfo
    if form.validate_on_submit():
        userinfo.phone = form.phone.data
        userinfo.grade = form.grade.data
        userinfo.department = form.department.data
        userinfo.school = form.school.data
        userinfo.major = form.major.data
        userinfo.qq = form.qq.data
        userinfo.introduction = form.introduction.data
        try:
            db.session.add(userinfo)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(str(e.orig).split('.')[1].capitalize() + ' is already existed!')
            return redirect(url_for('.user', username=userinfo.name))
        flash('信息修改成功！')
        return redirect(url_for('.user', username=userinfo.name))
    form.phone.data = userinfo.phone
    form.grade.data = userinfo.grade
    form.department.data = userinfo.department
    form.school.data = userinfo.school
    form.qq.data = userinfo.qq
    form.major.data = userinfo.major
    form.introduction.data = userinfo.introduction
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<uid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(uid):
    user = Account.query.get_or_404(uid)
    form = EditProfileAdminForm(user=user)
    userinfo = user.userinfo
    if form.validate_on_submit():
        userinfo.name = form.name.data
        userinfo.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        userinfo.phone = form.phone.data
        userinfo.student_id = form.student_id.data
        userinfo.grade = form.grade.data
        userinfo.department = form.department.data
        userinfo.school = form.school.data
        userinfo.major = form.major.data
        userinfo.qq = form.qq.data
        userinfo.introduction = form.introduction.data
        try:
            db.session.add(userinfo)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(str(e.orig).split('.')[1].capitalize() + ' is already existed!')
            return redirect(url_for('.user', username=userinfo.name))
        flash('信息修改成功！')
        return redirect(url_for('.user', username=userinfo.name))
    form.name.data = userinfo.name
    form.email.data = userinfo.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.phone.data = userinfo.phone
    form.student_id.data = userinfo.student_id
    form.grade.data = userinfo.grade
    form.department.data = userinfo.department
    form.school.data = userinfo.school
    form.qq.data = userinfo.qq
    form.major.data = userinfo.major
    form.introduction.data = userinfo.introduction
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=Account.query.get(post.author_uid)
        )
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / current_app.config['FLASK_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.cred_at.asc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>')
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user.uid != post.author_uid and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('更新动态成功！')
        return redirect(url_for('post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.cred_at.desc()).paginate(
        page, per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (query.statement, query.parameters,
                                                                                  query.duration, query.context))
    return response
