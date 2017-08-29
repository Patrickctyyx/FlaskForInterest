from webapp.extensions import celery
import os
import smtplib
from email.mime.text import MIMEText
from webapp.models import Reminder


@celery.task
def log(msg):
    return msg


@celery.task
def multiply(x, y):
    return x * y


@celery.task(
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=5
)
def remind(self, pk):
    mail_host = 'smtp.sina.com'
    mail_user = os.environ.get('MAIL_USERNAME')
    mail_pswd = os.environ.get('MAIL_PASSWORD')

    reminder = Reminder.query.get(pk)

    msg = MIMEText(reminder.text)
    msg['Subject'] = 'Your reminder'
    msg['From'] = mail_user
    msg['To'] = reminder.email

    try:
        # 创建smtp实例，用smtp协议发邮件
        s = smtplib.SMTP()
        # 连接服务器，这里是新浪的
        s.connect(mail_host, 25)
        # 登陆账号，不然怎么发呢
        s.login(mail_user, mail_pswd)
        # 发邮件
        # 还有另外一种s.send_mail(sender, receiver)
        s.send_message(msg)
        # 随手关闭服务器是个好习惯哦
        s.quit()

        return
    except Exception as e:
        self.retry(exc=e)


def on_reminder_save(mapper, connect, self):
    remind.apply_async(args=(self.id,), eta=self.date)
