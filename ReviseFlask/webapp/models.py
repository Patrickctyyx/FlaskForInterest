import datetime
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from flask_mongoengine import MongoEngine
from .extensions import bcrypt
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

db = SQLAlchemy()
mongo = MongoEngine()

tags = db.Table('post_tags',
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )


roles = db.Table('role_users',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('role.id', db.Integer, db.ForeignKey('role.id'))
                 )


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name='default'):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('user', lazy='dynamic')
    )

    def __init__(self, username):
        self.username = username
        default = Role.query.filter_by(name='default').first()
        self.roles.append(default)

    def __repr__(self):
        return '<User \'{}\'>'.format(self.username)

    @property
    def passwd(self):
        raise AttributeError('密码不可读！')

    @passwd.setter
    def passwd(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user


class AnomousUser(AnonymousUserMixin):
    pass


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text)
    publish_time = db.Column(db.DateTime, default=datetime.datetime.now)

    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Post \'{}\'>'.format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment \'{}\'>'.format(self.text[:15])


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Tag \'{}\'>'.format(self.title)

available_roles = ('admin', 'poster', 'default')


class Userm(mongo.Document):
    username = mongo.StringField(require=True)
    password = mongo.StringField(require=True)
    roles = mongo.ListField(mongo.StringField(choices=available_roles))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Commentm(mongo.EmbeddedDocument):
    name = mongo.StringField(require=True)
    text = mongo.StringField(require=True)
    date = mongo.DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Postm(mongo.Document):
    title = mongo.StringField(require=True)
    publish_date = mongo.DateTimeField(default=datetime.datetime.now())
    user = mongo.ReferenceField(Userm)
    comments = mongo.ListField(mongo.EmbeddedDocumentField(Commentm))
    tags = mongo.ListField(mongo.StringField())

    meta = {'allow_inheritance': True}

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class BlogPost(Postm):
    text = mongo.StringField(require=True)

    @property
    def type(self):
        return 'blog'


class VideoPost(Postm):
    url = mongo.StringField(require=True)

    @property
    def type(self):
        return 'video'


class ImagePost(Postm):
    image_url = mongo.ImageField(require=True)

    @property
    def type(self):
        return 'image'


class QuotePost(Postm):
    quote = mongo.StringField(require=True)
    author = mongo.StringField(require=True)

    @property
    def type(self):
        return 'quote'
