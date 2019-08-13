from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
import time
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'haima_login.settings')
django.setup()

#创建一个Celery实例
app = Celery("celery_tasks.tasks", broker="redis://139.224.114.75:6379/4")

@app.task()
def send_register_active_email(to_email, username, token):
    #发送邮件
    subject = "天天生鲜欢迎你"  # 邮件标题
    message = ''  # 邮件正文
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [to_email]  # 收件人
    html_message = """           <h1>%s  恭喜您成为海马生鲜注册会员</h1><br/><h3>请您在1小时内点击以下链接进行账户激 活</h3><a href="http://127.0.0.1:8000/haima/active/%s">http://127.0.0.1:8000/user/active/%s</a> """ % (username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    #为了体现出celery一步完成发送邮件，这里睡眠5秒
    time.sleep(5)