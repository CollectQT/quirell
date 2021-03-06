'''cms.py'''

# builtin
import hashlib
import multiprocessing
from glob import glob
# external
import flask
import redis
import markdown
import flask_login
import flask_cache
import flask_misaka
import itsdangerous
import flask_bcrypt
import flask_assets
import flask_session
import flask_seasurf
import flask_compress
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

    def __bool__(self):
        return False

class Cms(object):
    '''
    manages content and scripts for the webapp layer or the applications
    '''

    def __init__ (self, app):
        app.config.update(CONFIG)
        self._build_css(app.debug)

        # database
        try:
            self.db = Database()
            LOG.debug('Connected to neo4j database at {}'.format(os.environ['GRAPHENEDB_URL']))
        except:
            raise Exception('Could not connect to neo4j database')

        # sessions
        try:
            self.redis = redis.from_url(os.environ['REDISTOGO_URL'])
            app.config['SESSION_REDIS'] = self.redis
            LOG.debug('Connected to redis database at {}'.format(os.environ['REDISTOGO_URL']))
            flask_session.Session(app)
        except KeyError:
            raise Exception('Could not get REDISTOGO_URL')

        # content building
        flask_misaka.Misaka(app) # markdown
        app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension') # html preprocessor
        flask_compress.Compress(app) # gzip compression
        cache = flask_cache.Cache(app, # response caching
            config={
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_URL': os.environ['REDISTOGO_URL']
            }
        )
        self.cached = cache.cached; self.memoize = cache.memoize
        self.asset_builder(app) # asset compression

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

    def asset_builder(self, app):
        self.js_files = [path.split('quirell/webapp')[-1] for path in sorted(glob(BASE_PATH+'/quirell/webapp/static/js/libs/*'))]
        _js_files = [path.split('static/')[-1] for path in self.js_files]
        assets = flask_assets.Environment(app)
        js_bundle = flask_assets.Bundle(
            *_js_files,
            filters='jsmin',
            output='js/libs/packed.js'
        )
        assets.register('js_all', js_bundle)

    def _build_css(self, watch):
        if watch:
            # build css on changes
            from watchdog.events import FileSystemEventHandler
            class If_scss_changes (FileSystemEventHandler):
                def on_modified (self, event): Cms.build_css()

            # monitor for changes
            from watchdog.observers import Observer
            watch = Observer()
            watch.schedule(If_scss_changes(), BASE_PATH+'/quirell/webapp/static/scss/')
            watch.start()

            LOG.info('Watching /quirell/webapp/static/scss/ for changes')

        Cms.build_css()

    @staticmethod
    def build_css():
        import subprocess

        args = {
            'source': BASE_PATH+'/quirell/webapp/static/scss/main.scss',
            'output': BASE_PATH+'/quirell/webapp/static/css/main.css',
        }
        subprocess.call('''
            sassc -m {source} {output} -s compressed
            '''.format(**args),
            shell=True,
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE
        )
        LOG.info('Built CSS')

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

    def _before_request(self):
        if not flask.request.endpoint in ['static', 'base_static']:
            LOG.info('('+flask_login.current_user['username']+') '+flask.request.method+' '+str(flask.request.path)+' endpoint '+str(flask.request.endpoint)+'()')

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
            LOG.info('Tried to active account active account '+user['username'])
            return 'Account already active', 401
        else:
            LOG.info('Could not confirm account for input '+str(username or confirmation_code))
            return 'Could not confirm account', 401

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
