from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from ..models import Role, Account


class ContactMeForm(FlaskForm):

    name = StringField('姓名：', validators=[DataRequired()])
    email = StringField('邮箱：', validators=[DataRequired(), Email()])
    comment = TextAreaField('评论：')
    submit = SubmitField('提交')


class CompleteProfileField(FlaskForm):

    region = StringField('所在省：', validators=[DataRequired(), Length(2, 15)])
    gender = SelectField('性别：', validators=[DataRequired()], choices=[('M', '男'), ('F', '女')])
    introduction = TextAreaField('个人简介：')
    submit = SubmitField('提交')


class EditProfileField(FlaskForm):

    phone = StringField('电话号码：', validators=[DataRequired(), Length(0, 16)])
    region = StringField('所在省：', validators=[DataRequired(), Length(2, 15)])
    gender = SelectField('性别：', validators=[DataRequired()], choices=[('M', '男'), ('F', '女')])
    introduction = TextAreaField('个人简介：')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):

    username = StringField('用户名：', validators=[DataRequired()])
    email = StringField('邮箱：', validators=[DataRequired(), Email()])
    confirmed = BooleanField('确认信息:')
    role = SelectField('用户角色：', coerce=int)
    phone = StringField('电话号码:', validators=[DataRequired(), Length(10, 16)])
    region = StringField('所在省：', validators=[DataRequired(), Length(2, 15)])
    gender = SelectField('性别：', validators=[DataRequired()], choices=[('M', '男'), ('F', '女')])
    introduction = TextAreaField('自我介绍：')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                Account.query.filter_by(email=field.data).first():
            raise ValidationError('邮件已经存在！')


class PostForm(FlaskForm):

    body = PageDownField('Got some inspiration?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):

    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')
