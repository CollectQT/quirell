'''cms.py'''

# builtin
import os
import sys
import hashlib
# external
import markdown
import flask
# custom
from quirell.config import *
from quirell.database import Database

class Cms (object):

    def __init__ (self, app):
        import flask.ext.bcrypt as bcrypt
        import flask.ext.login as flask_login
        import flask.ext.misaka as misaka
        # configs
        for k,v in CONFIG.items(): app.config[k] = v
        # content building
        misaka.Misaka(app) # markdown
        self.build_css_automatic()
        # user management
        try: self.db = Database()
        except: print('[ERROR] Cannot connect to database')
        self.bcrypt = bcrypt.Bcrypt(app) # encryption
        self.login_manager =flask_login.LoginManager().init_app(app)
        self.user_container = dict()
        self.hash = hashlib.sha1()

    def clean_html (self, html):
        # cleans html to prevent people doing evil things with it like
        # like... idk. things with evil scripts and inline css
        from bs4 import BeautifulSoup
        html = BeautifulSoup(html)
        # destroy evil tags
        for tag in html(['iframe', 'script']): tag.decompose()
        # remove evil attributes
        for tag in html():
            for attribute in ["class", "id", "name", "style"]:
                del tag[attribute]
        return html

    #########
    # USERS #
    #########

    def user_exists (self, userID):
        result = self.db.get_user('@'+userID)
        if result == None: return False
        else: return True

    def add_user (self, userID, user):
        self.user_container[userID] = user
        print('[NOTE] Logging in user @'+userID)

    def get_user (self, userID):
        try: user = self.user_container[userID]
        except KeyError: user = None
        return user

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
