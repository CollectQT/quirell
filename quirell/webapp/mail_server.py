import time
import flask.ext.mail as flask_mail
from quirell.config import *

class Mail_server (object):
    '''mails things'''

    def __init__ (self, app, mail_queue):
        self.app = app
        self.mail = flask_mail.Mail(app)
        self.mail_queue = mail_queue
        self.mail_watcher()

    def mail_watcher(self):
        while True:
            if self.mail_queue.empty():
                time.sleep(1)
                continue
            print(self.mail_queue.get())
            self.send_mail()

    def send_mail(self):
        with self.app.app_context():
            msg = flask_mail.Message()
            msg.subject = '0130284108150816565'
            msg.recipients = ['firemagelynn@gmail.com']
            msg.body = 'rawr'
            msg.html = '<h1>rawr</h1>'
            self.mail.send(msg)
