'''cms.py'''

# external
import flask.ext.login as flask_login
# custom
from quirell.config import *

class Cms (object):
    def __init__ (self, app):
        from quirell.database import Database
        self.app = app
        # start things
        self.db = Database()
        self.attach_config()
        self.build_css_automatic()
        # attach stuff
        self.app.cms = self
        self.app.login_manager = self.login_manager()

    def start (self): return self.app

    def attach_config (self):
        from quirell.config import ENV
        self.app.config['SECRET_KEY'] = ENV['SECRET_KEY']

    # logins

    def login_manager (self):
        from flask.ext.login import LoginManager
        login_manager = LoginManager()
        login_manager.init_app(self.app)
        # configs, move them somewher else later
        login_manager.login_view = 'login'
        login_manager.login_message = 'You have to be logged in to view this page!'
        #
        return login_manager

    def user_loader (self, userID):
        '''
        returns user object when given a user_id
        should return None (not raise an exception) if the ID is not valid
        assums user is already logged in
        '''
        self.app.login_manager.user_loader = self.user_loader
        # not done ! needs more things !
        return self.db.get_user(userID)

    # css building

    def build_css_automatic (self):
        '''adds monitoring to autoreload css on changes'''
        # start up the monitor
        from watchdog import observers
        from watchdog.events import LoggingEventHandler
        change_monitor = Change_monitor(self)
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
        print(" * building css")

    # html building

    def quick_render (self, template, content, *args, **kwargs):
        '''render a webpage from text input and a template'''
        import flask
        return flask.render_template(template,
            html_content=self.convert_markdown(content), *args, **kwargs)

    def render (self, template, content, *args, **kwargs):
        '''render a webpage from a path file and a template'''
        import flask
        return flask.render_template(template,
            html_content=self.build_html(content), *args, **kwargs)

    def convert_markdown (self, text):
        import markdown
        md = markdown.Markdown()
        return md.convert(text)

    def build_html (self, file_name):
        '''
        input: path_name[.md|.html]
        html: <some html></some html>
        '''
        import os
        import glob
        import flask
        # get full path
        full_path = os.path.join(BASE_PATH, 'quirell', 'webapp', 'paths', file_name)
        # see what files start with that path
        files_with_path = glob.glob(full_path+'*')
        # if theres not just one, throw an error
        # if theres 0, its actually 404
        # if theres >1, someone shoud go rename some files ;p
        if not len(files_with_path) == 1:
            print('files with this path: '+str(len(files_with_path)))
            print('the above value should be 1')
            return flask.abort(404)
        # we've verified that theres only one file
        file_path = files_with_path[0]
        # open it
        with open(file_path, 'r') as file_data:
            file_text = file_data.read()
        # if its markdown, make it html
        if file_path.endswith('.md'):
            file_text = self.convert_markdown(file_text)
        # return the html
        return file_text

class User (flask_login.UserMixin):
    pass

from watchdog.events import FileSystemEventHandler
class Change_monitor (FileSystemEventHandler):
    ''' build_css() on scss file change'''
    def __init__ (self, cms_inst): self.css_builder = cms_inst.build_css
    def on_modified (self, event): self.css_builder()

def shutdown_server():
    from flask import request
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
