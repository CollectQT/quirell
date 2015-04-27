'''cms.py'''

# builtin
import hashlib
import multiprocessing
# external
import markdown
import itsdangerous
# custom
from quirell.config import *
from quirell.database import Database

class Cms (object):
    '''
    manages content and scripts for the webapp layer or the applications

    import with:
        from quirell.webapp import cms
    '''

    def __init__ (self, app):
        import flask.ext.bcrypt as bcrypt
        import flask.ext.login as flask_login
        import flask.ext.misaka as misaka
        import flask.ext.wtf.csrf as csrf
        # configs
        for k,v in CONFIG.items(): app.config[k] = v
        # database
        try: self.db = Database()
        except: print('[ERROR] Cannot connect to database')
        # content building
        misaka.Misaka(app) # markdown
        if app.config['DEBUG']: self.build_css_automatic()
        # users
        self.login_manager =flask_login.LoginManager().init_app(app)
        self.user_container = dict()
        # security
        self.hash = hashlib.sha1()
        self.bcrypt = bcrypt.Bcrypt(app)
        self.csrf = csrf.CsrfProtect(app)
        self.serialize = itsdangerous.URLSafeSerializer(app.config['SECRET_KEY'])
        # mails
        self.start_mail_server(app)

    ###########
    # GENERAL #
    ###########

    def clean_html (self, html):
        # cleans html to prevent people doing evil things with it like
        # like... idk. things with evil scripts and inline css
        from bs4 import BeautifulSoup
        html = BeautifulSoup(html)
        # destroy evil tags
        for tag in html(['iframe', 'script']): tag.decompose()
        # remove evil attributes
        for tag in html():
            for attribute in ["class", "id", "name", "style", "data"]:
                del tag[attribute]
        return str(html)

    #########
    # USERS #
    #########

    def get_user_page (self, user_self, user_req):
        '''
        generates a user page give a username for a requested user
        (user_req) and an object for a current user (user_self)

        returns user, timeline
        '''
        # format user_self so that user_self and user_req are strings
        if not user_self.is_authenticated(): user_self=''
        else: user_self = user_self['username']
        # run the appropriate db query
        # cases are: public, self, else
        #
        # if you were to run the else case (i.e. view_timeline)
        # on either "self" or "public" the results would be the same.
        # The only reason they get special cases is so that we aren't
        # making unneeded access checks. For example: you can always
        # view all of your own posts, so no need to check permissions
        if not user_self:
            return self.db.view_public_timeline(owner=user_req)
        elif user_self == user_req:
            return self.db.load_timeline(owner=user_req)
        else:
            return self.db.view_timeline(owner=user_req, reader=user_self)

    def user_exists (self, username):
        if not username[0] == '@': username = '@'+username
        result = self.db.load_user(username)
        if result == None: return False
        else: return True

    def add_user (self, username, user):
        self.user_container[username] = user
        print('[NOTE] Logging in user '+username)

    def get_logged_in_user (self, username):
        try: user = self.user_container[username]
        except KeyError: user = None
        return user

    def send_confirmation_email (self, username, url_root):
        user = self.db.load_user(username)
        if not user['active']:
            self.mail_queue.put(
                {'task': 'account confirmation',
                'inputs': {
                    'url_root': url_root,
                    'email': user['email'],
                    'display_name': user['display_name'],
                    'username': user['username'],
                    'confirmation_code': user['confirmation_code'],
                    },
                })
            return 'Sending confirmation email to {}'.format(user['email']), 200
        else:
            return 'Could not send confirmation email', 401

    def activate_account (self, confirmation_code='', username=''):
        # set user
        if confirmation_code:
            user = self.db.load_user_from_confirmation_code(confirmation_code)
        elif username:
            user = self.db.load_user(username)
        # do work on user
        if not user['active']:
            user['active'] = True
            user['confirmation_code'] = ''
            user.push()
            return 'Account actived!', 200
        elif user['active']:
            return 'Account already active', 401
        else:
            return 'Could not confirm account', 401

    ################
    # CSS BUILDING #
    ################

    from watchdog.events import FileSystemEventHandler
    class Change_monitor (FileSystemEventHandler):
        ''' build_css() on scss file change'''
        def __init__ (self, cms_inst): self.css_builder = cms_inst.build_css
        def on_modified (self, event): self.css_builder()


    def build_css_automatic (self):
        '''adds monitoring to autoreload css on changes'''
        # start up the monitor
        from watchdog import observers
        from watchdog.events import LoggingEventHandler
        change_monitor = Cms.Change_monitor(self)
        observer = observers.Observer()
        observer.schedule(change_monitor, BASE_PATH+'/quirell/webapp/static/scss/')
        observer.start()
        # start css writer
        import scss
        scss.config.PROJECT_ROOT = BASE_PATH
        self.scss_file = BASE_PATH+'/quirell/webapp/static/scss/main.scss'
        self.css_writer = scss.Scss()
        # do an intial build
        self.build_css()

    def build_css (self):
        '''builds css from sass'''
        with open(self.scss_file, 'r') as infile:
            scss_content = infile.read()
        compiled_css = self.css_writer.compile(scss_content)
        # readability sillyness
        for i in range(4): compiled_css = compiled_css.replace("  ", " ")
        # write to file
        with open(BASE_PATH+'/quirell/webapp/static/css/main.css', 'w') as outfile:
            outfile.write(compiled_css)
        # log
        print("[NOTE] Building CSS")

    ###########
    # Mailing #
    ###########

    def start_mail_server(self, app):
        from quirell.webapp.mail_server import Mail_server
        # mails go into the queue
        self.mail_queue = multiprocessing.SimpleQueue()
        # the process handles all the mails
        mail_process = multiprocessing.Process(target=Mail_server,
           args=(app, self.mail_queue))
        mail_process.start()
