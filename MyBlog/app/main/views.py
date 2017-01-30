from flask import render_template, redirect, url_for, flash, abort

from . import main
from .forms import ContactMeForm, CompleteProfileField, EditProfileField
from .. import db
from ..models import ContactMeInfo, UserInfo
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ContactMeForm()
    if form.validate_on_submit():
        info = ContactMeInfo.query.filter_by(phone=form.phone.data).first()
        if info is None:
            info = ContactMeInfo(name=form.name.data,
                                 phone=form.phone.data,
                                 email=form.email.data,
                                 comment=form.comment.data if form.comment.data else None)
            db.session.add(info)
            db.session.commit()
            try:
                db.session.commit()
            except:
                flash('由于玄学问题，提交失败。')
        else:
            flash('您已经提交过个人信息。')
        return redirect(url_for('.index'))  # 这里的.前面是命名空间，相当于main.index，表示是main这个蓝图下的
    return render_template('home.html', form=form)


@main.route('/user/<username>')
def user(username):
    user = UserInfo.query.filter_by(name=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


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
        db.session.add(userinfo)
        db.session.commit()
        flash('信息初始化完成！')
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
        db.session.add(userinfo)
        db.session.commit()
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
