import time
from flask.ext.mail import Mail
from quirell.config import *

class Mail_server (object):
    '''mails things'''

    def __init__ (self, app, mail_queue):
        mail = Mail(app)
        mail.init_app(app)
        self.mail_queue = mail_queue
        self.mail_watcher()

    def mail_watcher (self):
        while True:
            if self.mail_queue.empty():
                time.sleep(1)
                continue
            print(self.mail_queue.get())
