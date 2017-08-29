from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from .models import User


class CommentForm(FlaskForm):
    text = TextAreaField('评论', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('用户名', [DataRequired(), Length(max=255)])
    password = PasswordField('密码', [DataRequired()])
    remember_me = BooleanField('记住登录状态')

    def validate(self):  # 在 validate_on_submit 的时候会检查
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('用户名或密码错误')
            return False

        if not user.verify_password(self.password.data):
            self.username.errors.append('用户名或密码错误')
            return False

        return True


class RegisterForm(FlaskForm):
    username = StringField('用户名', [DataRequired(), Length(max=255)])
    password = PasswordField('密码', [DataRequired(), Length(min=8)])
    confirm = PasswordField('确认密码', [DataRequired(), EqualTo('password')])

    def validate(self):
        check_validate = super(RegisterForm, self).validate()

        if not check_validate:
            return False

        user = User.query.filter_by(username=self.username.data).first()

        if user:
            self.username.errors.append('用户名已经存在！')
            return False

        return True


class PostForm(FlaskForm):
    title = StringField('标题', [DataRequired(), Length(max=255)])
    text = TextAreaField('正文', [DataRequired()])


class ReminderForm(FlaskForm):
    date = StringField('日期', [DataRequired()])
    time = StringField('时间', [DataRequired()])
    email = StringField('邮箱', [DataRequired()])
    text = TextAreaField('提醒内容', [DataRequired()])

