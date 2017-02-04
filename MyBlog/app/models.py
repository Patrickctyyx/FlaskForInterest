from . import db
import uuid
import hashlib
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manger
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request


@login_manger.user_loader
def load_user(uid):
    return Account.query.get(uid)


class Verify:

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
    ADMINISTER = 0x80


class ContactMeInfo(db.Model):

    __tablename__ = 'Contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(64), unique=True)
    comment = db.Column(db.Text)

    def __repr__(self):
        return '<ContactMeInfo %d>' % self.id


class Account(db.Model, UserMixin):

    __tablename__ = 'Account'

    uid = db.Column(db.String(36), primary_key=True,
                    default=lambda: str(uuid.uuid4()))  # 用uuid应该是为了防止用户名冲突
    passwd = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.now)  # default可以接受函数为参数
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'))
    # 两边都要引用就用back_populates
    userinfo = db.relationship('UserInfo', back_populates='account', uselist=False)  # uselist=False表示一对一
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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
            info = UserInfo(uid=u.uid,
                            email=forgery_py.internet.email_address(),
                            name=forgery_py.name.full_name())
            db.session.add(info)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manger.anonymous_user = AnonymousUser


class UserInfo(db.Model):

    __tablename__ = 'UserInfo'

    uid = db.Column(db.String(36), db.ForeignKey(Account.uid), primary_key=True)
    avatar_hash = db.Column(db.String(32))
    name = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(64), unique=True)
    student_id = db.Column(db.Integer, unique=True)
    grade = db.Column(db.String(64))
    department = db.Column(db.String(128))
    school = db.Column(db.String(128))
    major = db.Column(db.String(128))
    qq = db.Column(db.String(64), unique=True)
    introduction = db.Column(db.Text)

    account = db.relationship('Account', back_populates='userinfo', uselist=False)

    def __init__(self, **kwargs):
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://s.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class Role(db.Model):

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
    cred_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    author_uid = db.Column(db.String(36), db.ForeignKey(Account.uid))

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
