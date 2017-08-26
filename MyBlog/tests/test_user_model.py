import unittest
import time
from app.models import Account, UserInfo, Verify, Role, Permission, AnonymousUser
from app import db, create_app


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()  # 相当于创建了context
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        a = Account(password='pat')
        self.assertTrue(a.passwd is not None)

    def test_no_password_getter(self):
        a = Account(password='pat')
        with self.assertRaises(AttributeError):
            a.password

    def test_password_verification(self):
        a = Account(password='pat')
        self.assertTrue(a.verify_password('pat'))
        self.assertFalse(a.verify_password('cty'))

    def test_password_are_random(self):
        a = Account(password='pat')
        a1 = Account(password='pat')
        self.assertFalse(a.passwd == a1.passwd)

    def test_confirmation_token(self):
        a1 = Account(password='aaa')
        a2 = Account(password='bbb')
        db.session.add(a1)
        db.session.add(a2)
        db.session.commit()
        token = a1.generate_confirmation_token()
        self.assertFalse(a2.confirm(token))
        self.assertTrue(a1.confirm(token))

    def test_expired_confirmation_token(self):
        a1 = Account(password='aaa')
        db.session.add(a1)
        db.session.commit()
        token = a1.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(a1.confirm(token))

    def test_forget_password_verification(self):
        ver1 = Verify('email@email.com')
        token = ver1.generate_confirmation_token()
        ver2 = Verify('email@email.com')
        self.assertTrue(ver2.confirm(token))

    def test_wrong_email_password_verification(self):
        ver1 = Verify('email@email.com')
        token = ver1.generate_confirmation_token()
        ver2 = Verify('wrongemail@email.com')
        self.assertFalse(ver2.confirm(token))

    def test_roles_and_permissions(self):
        Role.insert_roles()
        a = Account(password='cat')
        self.assertTrue(a.can(Permission.WRITE_ARTICLES))
        self.assertFalse(a.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
