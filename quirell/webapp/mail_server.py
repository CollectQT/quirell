import time
import flask_mail as flask_mail
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
            kwargs = self.mail_queue.get()
            if kwargs['task'] == 'shutdown':
                LOG.info('[NOTE] Shutting Down Mailer')
                break
            elif kwargs['task'] == 'account confirmation':
                LOG.info('Sending account confirmation email')
                self.send_account_confirmation_email(kwargs['inputs'])

    def send_mail(self):
        with self.app.app_context():
            msg = flask_mail.Message()
            msg.subject = '0130284108150816565'
            msg.recipients = ['firemagelynn@gmail.com']
            msg.body = 'rawr'
            msg.html = '<h1>rawr</h1>'
            self.mail.send(msg)

    def send_account_confirmation_email(self, inputs):
        with self.app.app_context():
            msg = flask_mail.Message()
            msg.subject = 'Confirm Your Quirell Account'
            msg.recipients = [inputs['email']]
            # msg.html = ''
            msg.body = '''
Hey {display_name}!

Confirm you account on Quirell by going to the link below:

{url_root}confirm_account/{confirmation_code}
                '''.format(display_name=inputs['display_name'],
                    username=inputs['username'],
                    confirmation_code=inputs['confirmation_code'],
                    url_root=inputs['url_root'])
            self.mail.send(msg)
