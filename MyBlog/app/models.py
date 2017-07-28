from . import db
import uuid
import hashlib
import datetime
import bleach
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manger
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from app.exception import ValidationError


@login_manger.user_loader
def load_user(uid):
    return Account.query.get(uid)


class Verify:

    """Verify when password is forgotten."""

    def __init__(self, email):
        self.email = email

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.email})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.email:
            return False
        return True


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x0f


class ContactMeInfo(db.Model):

    __tablename__ = 'Contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(16))
    email = db.Column(db.String(64))
    comment = db.Column(db.Text)

    def __repr__(self):
        return '<ContactMeInfo %d>' % self.id


class Account(db.Model, UserMixin):

    """
    User table
    重要的信息比如邮箱（用于登录验证），密码应该存放在这里。
    和登录相关的内容比如用户名，上次登录，登录 ip 之类都应该存放在这个表。
    账号是否验证，权限也应该放在这里。
    """

    __tablename__ = 'Account'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))  # 用 uuid 应该是为了防止用户名冲突
    email = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(32), unique=True)
    phone = db.Column(db.String(16), unique=True)
    passwd = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.now)  # default 可以接受函数为参数
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'))

    # 两边都要引用就用 back_populates
    userinfo = db.relationship('UserInfo', back_populates='account', uselist=False)  # uselist=False 表示一对一
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property  # 只读函数
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.passwd = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.passwd, password)

    def get_id(self):
        return str(self.uid)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.uid})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.uid:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def ping(self):
        self.last_seen = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = Account(uid=str(uuid.uuid4()),
                        password=forgery_py.lorem_ipsum.word(),
                        confirmed=True)
            db.session.add(u)
            db.session.flush()
            info = UserInfo()
            info.uid = u.uid
            info.email = forgery_py.internet.email_address()
            info.name = forgery_py.name.full_name()
            db.session.add(info)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'uid': self.uid})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Account.query.get(data['uid'])


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manger.anonymous_user = AnonymousUser


class UserInfo(db.Model):

    """
    User information table
    存放不那么重要的信息，比如头像介绍等。
    通过 uid 来与用户表关联
    """

    __tablename__ = 'UserInfo'

    uid = db.Column(db.String(36), db.ForeignKey(Account.uid), primary_key=True)
    avatar_hash = db.Column(db.String(32))
    region = db.Column(db.String(16))
    gender = db.Column(db.String(8))
    introduction = db.Column(db.Text)

    account = db.relationship('Account', back_populates='userinfo', uselist=False)

    def __init__(self, **kwargs):
        self.uid = kwargs['uid']
        email = Account.query.filter_by(uid=kwargs['uid']).first().email
        if email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://s.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def to_json(self):
        json_user = {
            'region': self.region,
            'gender': self.gender,
            'introduction': self.introduction,
            'cred_at': self.account.cred_at,
            'last_seen': self.account.last_seen
        }
        return json_user


class Role(db.Model):

    """
    User kind
    分为用户，小管理员，管理员
    """

    __tablename__ = 'Role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('Account', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Post(db.Model):

    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    cred_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    author_uid = db.Column(db.String(36), db.ForeignKey(Account.uid))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = Account.query.count()
        for i in range(count):
            u = Account.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     cred_at=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        # markdown()把Markdown文本转换为html
        # 然后用bleach.clean()来删除不在白名单的标签
        # 最后bleach.linkify()把纯文本链接转化为<a>链接
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'cred_at': self.cred_at,
            # 'author': url_for('api.get_user', uid=self.author_uid, _external=True),
            # 'comments': url_for('api_get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def fron_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('Post does not have a body')
        return Post(body=body)


class Comment(db.Model):

    __tablename__ = 'Comment'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    cred_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.String(36), db.ForeignKey(Account.uid))
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

# 添加到sqlalchemy的监视中，只要Post的body字段设置新值，函数就会自动调用
db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_change_body)
