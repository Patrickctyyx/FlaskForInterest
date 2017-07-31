from selenium import webdriver
import unittest
import threading
from app import db, create_app
from app.models import Role, Account, Post, UserInfo


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Chrome('/home/patrick/Softwares/chromedriver')
        except:
            pass

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            Account.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = Account(password='aaa',
                            username='patrick',
                            email='chengtianyang523@sina.com',
                            confirmed=True)
            db.session.add(admin)
            db.session.flush()
            userinfo = UserInfo(uid=admin.uid)
            userinfo.role = admin_role
            db.session.add(userinfo)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://127.0.0.1:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        response = self.client.get('http://127.0.0.1:5000/')
        self.assertTrue('<h2 class="tm-gold-text tm-title">Patrick\'s Space</h2>' in self.client.page_source)

        self.client.find_element_by_link_text('登录').click()
        self.assertTrue('<h2 class="tm-gold-text tm-title">登录</h2>' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('chengtianyang523@sina.com')
        self.client.find_element_by_name('password').send_keys('aaa')
        self.client.find_element_by_name('submit').click()
        self.assertTrue('<h2 class="tm-gold-text tm-title">Patrick\'s Space</h2>' in self.client.page_source)

        self.client.find_element_by_link_text('个人信息').click()
        self.assertTrue(self.client.title == 'Patrick\'s Space - Complete Profile')


