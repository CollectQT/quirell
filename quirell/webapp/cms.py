'''cms.py'''

class Cms (object):
    def __init__ (self, app):
        self.app = app
        self.build_css_automatic()
        self.app.login_manager = self.login_manager()
        self.app.cms = self

    def start (self): return self.app

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
        compiled_css = self.css_writer.compile(self.scss_file)
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
            html_content=build_html(os.path.join(self.app.root_path, content)),
            *args, **kwargs)

from watchdog.events import FileSystemEventHandler
class Change_monitor (FileSystemEventHandler):
    ''' build_css() on scss file change'''
    def __init__ (self, cms_inst): self.cms_inst = cms_inst
    def on_modified (self, event): self.cms_inst()

def build_html (path):
    '''
    input: path_name[.md|.html]
    html: <some html></some html>
    '''
    # try for markdown
    try:
        with open(path+'.md', 'r') as md_data:
            text = md_data.read()
        # create html
        import markdown
        md = markdown.Markdown()
        return md.convert(text)
    except IOError: pass
    # try for html
    try:
        with open(path+'.html', 'r') as html_data:
            text = html_data.read()
        return text
    # if neither? fail
    except IOError: return 'something broke???'
