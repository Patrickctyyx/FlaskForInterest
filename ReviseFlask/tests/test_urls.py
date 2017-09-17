import unittest
from webapp import create_app
from webapp.models import db, Role, User


class TestURLs(unittest.TestCase):
    def setUp(self):
        app = create_app('test')
        self.client = app.test_client()
        db.app = app

        db.create_all()

        test_role = Role('default')
        db.session.add(test_role)
        db.session.flush()

        test_user = User('test')
        test_user.passwd = 'test'
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register(self):
        result = self.client.post(
            '/register',
            data=dict(username='test', password='test'),
            follow_redirects=True
        )
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Patrick\'s Space - Login', result.data)


if __name__ == '__main__':
    unittest.main()
