from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import Account, UserInfo


class LoginForm(FlaskForm):

    email = StringField('邮箱:', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('密码:', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('确认登录')


class RegisterForm(FlaskForm):

    email = StringField('邮箱：', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('用户名：', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('电话号码：', validators=[DataRequired(), Length(11, 11)])
    password = PasswordField('密码：', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('重复密码：', validators=[DataRequired()])
    submit = SubmitField('确认注册')

    def validate_email(self, field):
        if Account.query.filter_by(email=field.data).first():
            raise ValidationError('已经存在的邮箱。')


class ChangePassForm(FlaskForm):

    former_pass = PasswordField('原密码:', validators=[DataRequired()])
    password = PasswordField('新密码:', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('重复密码:', validators=[DataRequired()])
    submit = SubmitField('确认更改')


class VerifyEmailForm(FlaskForm):

    email = StringField('Email:', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Submit')


class ResetPassForm(FlaskForm):

    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Confirm')
