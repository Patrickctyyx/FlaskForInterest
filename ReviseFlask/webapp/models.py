import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from .extensions import bcrypt

db = SQLAlchemy()

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
