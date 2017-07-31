import unittest
from flask import url_for
from app import create_app, db
from app.models import Role, UserInfo, Account


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertFalse('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'), data={
            'email': 'chengtiyanyang@gmail.com',
            'username': 'patrick',
            'phone': '15521164491',
            'password': 'aaa',
            'password2': 'aaa'
        })
        self.assertTrue(response.status_code == 302)

        response = self.client.post(url_for('auth.login'), data={
            'email': 'chengtiyanyang@gmail.com',
            'password': 'aaa'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('您还没有验证您的账号' in data)

        user = Account.query.filter_by(email='chengtiyanyang@gmail.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('你的账户已经成功确认' in data)

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('您已经成功登出。' in data)
