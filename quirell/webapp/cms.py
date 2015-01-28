'''cms.py'''

# builtin
import sys
# external
import markdown
import flask
import flask.ext.bcrypt as bcrypt
import flask.ext.login as flask_login
# custom
from quirell.config import *
from quirell.database import Database

class Cms (object):

    def __init__ (self, app):
        app.cms = self
        # configs
        for k,v in CONFIG.items(): app.config[k] = v
        # content building
        self.md = markdown.Markdown()
        self.build_css_automatic()
        # user management
        # connect to user database
        try: self.db = Database()
        except:
            print('[ERROR] Cannot connect to database')
            #print('[WARNING] Running without database, if you need a database connection you should run "python -m quirell.webapp.shutdown"')
        self.bcrypt = bcrypt.Bcrypt(app)
        self.login_manager =flask_login.LoginManager().init_app(app)
        self.user_container = dict()

    #########
    # USERS #
    #########

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

    #################
    # HTML BUILDING #
    #################

    def form_render (self, template, form, *args, **kwargs):
        '''render a page from a template and a form's html attribute'''
        html_content = flask.templating.render_template_string(form.html, form=form)
        return flask.render_template(template, form=form, html_content=html_content,
            *args, **kwargs)

    def text_render (self, template, content, *args, **kwargs):
        '''render a page from text input and a template file'''
        html_content=self.md.convert(content)
        return flask.render_template(template, html_content=html_content, *args, **kwargs)

    def file_render (self, template, file_path='', *args, **kwargs):
        '''render a page from a path file and a template file'''
        html_content=self.html_from_file(file_path)
        return flask.render_template(template, html_content=html_content, *args, **kwargs)

    def html_from_file (self, file_path):
        '''input: path_name[.md|.html]; output: <some html></some html>'''
        import os
        import glob
        import flask
        # get full path
        file_path = os.path.join(BASE_PATH, 'quirell', 'webapp', 'templates', file_path)
        # see what files start with that path
        # if theres not just one, we have issues
        files_with_path = glob.glob(file_path+'*')
        # if theres >1, someone shoud go rename some files ;p
        # but thats not always reasonable, so we search a bit more for the file
        if len(files_with_path) > 1:
            if len(glob.glob(file_path+'.md')) == 1:
                files_with_path = glob.glob(file_path+'.md')
            elif len(glob.glob(file_path+'.html')) == 1:
                files_with_path = glob.glob(file_path+'.html')
            else:
                print('[NOTE] There are files starting with path '+str(file_path))
                print('[NOTE] But that path does not define a single markdown or HTML file')
                print('[NOTE] 404ing request')
                return flask.abort(404)
        # if theres 0, no file is found, tell flask we are 404ing
        elif len(files_with_path) == 0:
            print('[NOTE] No files with path '+str(file_path)+': '+str(len(files_with_path)))
            print('[NOTE] 404ing request')
            return flask.abort(404)
        # we've verified that theres only one file
        file_path = files_with_path[0]
        # open it
        with open(file_path, 'r') as file_data:
            file_text = file_data.read()
        # if its markdown, make it html
        if file_path.endswith('.md'):
            file_text = self.md.convert(file_text)
        # return the html
        return file_text
