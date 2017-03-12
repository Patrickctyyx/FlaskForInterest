from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from ..models import Role, UserInfo


class ContactMeForm(FlaskForm):

    name = StringField('Name:', validators=[DataRequired()])
    phone = StringField('Phone Number:', validators=[DataRequired(), Length(11, 11)])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    comment = TextAreaField('Comment:')
    submit = SubmitField('Submit')


class CompleteProfileField(FlaskForm):

    phone = StringField('Phone:', validators=[DataRequired(), Length(10, 16)])
    student_id = IntegerField('Student ID:', validators=[DataRequired(), NumberRange(1000000000, 3000000000)])
    grade = StringField('Grade:', validators=[DataRequired()])
    department = StringField('Department:', validators=[DataRequired()])
    school = StringField('School:', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    qq = StringField('QQ:', validators=[DataRequired()])
    introduction = TextAreaField('Introduction:')
    submit = SubmitField('Submit')


class EditProfileField(FlaskForm):

    phone = StringField('Phone:', validators=[DataRequired(), Length(0, 16)])
    grade = StringField('Grade:', validators=[DataRequired()])
    department = StringField('Department:', validators=[DataRequired()])
    school = StringField('School:', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    qq = StringField('QQ:', validators=[DataRequired()])
    introduction = TextAreaField('Introduction:')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):

    name = StringField('Name:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    confirmed = BooleanField('Confirmed:')
    role = SelectField('Role', coerce=int)
    phone = StringField('Phone:', validators=[DataRequired(), Length(10, 16)])
    student_id = IntegerField('Student ID:', validators=[DataRequired(), NumberRange(1000000000, 3000000000)])
    grade = StringField('Grade:', validators=[DataRequired()])
    department = StringField('Department:', validators=[DataRequired()])
    school = StringField('School:', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    qq = StringField('QQ:', validators=[DataRequired()])
    introduction = TextAreaField('Introduction:')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.userinfo.email and \
                UserInfo.query.filter_by(email=field.data).first():
            raise ValidationError('Email已经存在！')


class PostForm(FlaskForm):

    body = PageDownField('Got some inspiration?', validators=[DataRequired()])
    submit = SubmitField('Submit')
