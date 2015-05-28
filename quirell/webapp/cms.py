'''cms.py'''

# builtin
import hashlib
import multiprocessing
# external
import flask
import redis
import markdown
import flask_login
import flask_misaka
import itsdangerous
import flask_bcrypt
import flask_assets
import flask_session
import flask_seasurf
# custom
from quirell.config import *
from quirell.database import Database

def load_user(username):
    from quirell.webapp.models import User
    return User().get(username)

class Anon(flask_login.AnonymousUserMixin):
    '''functions for people not logged in'''

    def __getitem__ (self, key):
        if key == 'username':
            return 'anonymous'
        else:
            return ''

class Cms(object):
    '''
    manages content and scripts for the webapp layer or the applications
    '''

    def __init__ (self, app):
        app.config.update(CONFIG)
        # database
        try:
            self.db = Database()
            LOG.info('Connected to neo4j database')
        except:
            raise Exception('Could not connect to neo4j database')
        # sessions
        try:
            app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDISTOGO_URL'])
            LOG.info('Connected to redis database')
            flask_session.Session(app)
        except KeyError:
            raise Exception('Could not get REDISTOGO_URL')
        # content building
        flask_misaka.Misaka(app) # markdown
        if app.config['DEBUG']: self.build_css_automatic()
        assets = flask_assets.Environment(app)
        # users
        self.login_manager = flask_login.LoginManager()
        self.login_manager.init_app(app)
        self.login_manager.anonymous_user = Anon
        self.login_manager.user_loader(load_user)
        # security
        self.hash = hashlib.sha1()
        self.bcrypt = flask_bcrypt.Bcrypt(app)
        self.csrf = flask_seasurf.SeaSurf(app)
        self.serialize = itsdangerous.URLSafeSerializer(app.config['SECRET_KEY'])
        # mails
        self.start_mail_server(app)
        # logging
        app.before_request(self._before_request)
        # app.after_request(self._after_request)

    def _before_request(self):
        if not flask.request.endpoint in ['static', 'base_static']:
            LOG.info('('+flask_login.current_user['username']+') '+flask.request.method+' '+flask.request.path+' endpoint '+flask.request.endpoint+'()')

    # def _after_request(self, r):
    #     return r

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
        if (user) and (not user['active']):
            user['active'] = True
            user['confirmation_code'] = ''
            user.push()
            LOG.info('Activating account '+user['username'])
            return 'Account actived!', 200
        elif (user) and (user['active']):
            return 'Account already active', 401
        else:
            return 'Could not confirm account', 401

    ################
    # CSS BUILDING #
    ################

    from watchdog.events import FileSystemEventHandler
    class _Change_monitor (FileSystemEventHandler):
        ''' build_css() on scss file change'''
        def __init__ (self, cms_inst): self.css_builder = cms_inst.build_css
        def on_modified (self, event): self.css_builder()


    def build_css_automatic (self):
        '''adds monitoring to autoreload css on changes'''
        # start up the monitor
        from watchdog import observers
        from watchdog.events import LoggingEventHandler
        change_monitor = Cms._Change_monitor(self)
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
        LOG.info('Building CSS')

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
        LOG.info('Starting Mail Server')
