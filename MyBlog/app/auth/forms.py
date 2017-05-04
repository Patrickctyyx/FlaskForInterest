from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import Account, UserInfo


class LoginForm(FlaskForm):

    email = StringField('Email:', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):

    email = StringField('Email:', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('User Name:', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('Phone Number:', validators=[DataRequired(), Length(11, 11)])
    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if Account.query.filter_by(email=field.data).first():
            raise ValidationError('已经存在的邮箱。')


class ChangePassForm(FlaskForm):

    former_pass = PasswordField('Your Former Password:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class VerifyEmailForm(FlaskForm):

    email = StringField('Email:', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Submit')


class ResetPassForm(FlaskForm):

    password = PasswordField('Password:', validators=[DataRequired(), EqualTo('password2', message='两次密码应该相同。')])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Confirm')
