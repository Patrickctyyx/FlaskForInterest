from webapp.extensions import celery
import os
import smtplib
import datetime
from flask import render_template
from email.mime.text import MIMEText
from webapp.models import Reminder
from webapp.models import Post, Contact


def sendMail(subject, body, msg_to):

    mail_host = 'smtp.sina.com'
    mail_user = os.environ.get('MAIL_USERNAME')
    mail_pswd = os.environ.get('MAIL_PASSWORD')

    # 创建一个空邮件，下面就是放入内容
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.environ.get('MAIL_USERNAME')
    msg['To'] = msg_to

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

    reminder = Reminder.query.get(pk)

    try:
        sendMail('Your reminder', reminder.text, reminder.email)

        return
    except Exception as e:
        self.retry(exc=e)


def on_reminder_save(mapper, connect, self):
    remind.apply_async(args=(self.id,), eta=self.date)


@celery.task(
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=5
)
def digest(self):
    year, week = datetime.datetime.now().isocalendar()[0: 2]
    date = datetime.date(year, 1, 1)
    if date.weekday() > 3:
        date += datetime.timedelta(days=7-date.weekday())
    else:
        date -= datetime.timedelta(days=datetime.weekday())
    delta = datetime.timedelta(days=(week - 1) * 7)
    start, end = date + delta, date + delta + datetime.timedelta(days=6)

    posts = Post.query.filter(
        Post.publish_time >= start,
        Post.publish_time <= end
    ).all()

    if len(posts) == 0:
        return

    mail_host = 'smtp.sina.com'
    mail_user = os.environ.get('MAIL_USERNAME')
    mail_pswd = os.environ.get('MAIL_PASSWORD')

    # 创建一个空邮件，下面就是放入内容
    msg = MIMEText(
        render_template('digest.html', posts=posts),
        'html'
    )
    msg['Subject'] = 'Weekly digest'
    msg['From'] = os.environ.get('MAIL_USERNAME')
    recipients = Contact.query.all()
    # 也可以这样直接查找无重复的 email
    # recipients = db.session.query(Contact.email).distinct().all()
    # 但是返回的 email 是 tuple 中的第一个元素，因此要把它取出来...
    if len(recipients) == 0:
        return
    recipients = list(set(recipients))
    msg['To'] = recipients

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
