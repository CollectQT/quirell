'''cms.py'''

from quirell.config import *

class Cms (object):
    def __init__ (self, app):
        # attach stuff
        self.app = app
        self.app.cms = self
        # start things
        self.attach_config()
        self.build_css_automatic()
        self.app.login_manager = self.login_manager()

    def start (self): return self.app

    def attach_config (self):
        from quirell.config import ENV
        self.app.config['SECRET_KEY'] = ENV['SECRET_KEY']

    def login_manager (self):
        from flask.ext.login import LoginManager
        login_manager = LoginManager()
        login_manager.init_app(self.app)
        return login_manager

    # css building

    def build_css_automatic (self):
        '''adds monitoring to autoreload css on changes'''
        # start up the monitor
        from watchdog import observers
        from watchdog.events import LoggingEventHandler
        change_monitor = Change_monitor(self)
        observer = observers.Observer()
        observer.schedule(change_monitor, self.app.root_path+'/static/scss/')
        observer.start()
        # start css writer
        import scss
        scss.config.PROJECT_ROOT = self.app.root_path
        self.scss_file = self.app.root_path+'/static/scss/main.scss'
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
        with open(self.app.root_path+'/static/css/main.css', 'w') as outfile:
            outfile.write(compiled_css)
        # log
        print(" * building css")

    # html building

    def render (self, template, content, *args, **kwargs):
        import os
        import flask
        return flask.render_template(template,
            html_content=self.build_html(content), *args, **kwargs)

    def build_html (self, file_name):
        '''
        input: path_name[.md|.html]
        html: <some html></some html>
        '''
        import os
        import glob
        import flask
        import markdown
        # get full path
        full_path = os.path.join(BASE_PATH, 'quirell', 'webapp', 'paths', file_name)
        print(full_path)
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
            md = markdown.Markdown()
            file_text = md.convert(file_text)
        # return the html
        return file_text

from watchdog.events import FileSystemEventHandler
class Change_monitor (FileSystemEventHandler):
    ''' build_css() on scss file change'''
    def __init__ (self, cms_inst): self.cms_inst = cms_inst
    def on_modified (self, event): self.cms_inst()
