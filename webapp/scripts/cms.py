def build_css (app):
    '''
    builds css from sass
    '''
    import scss
    # configs
    scss.config.PROJECT_ROOT = app.root_path
    # init
    css = scss.Scss()
    compiled_css = css.compile(scss_file=app.root_path+'/static/scss/main.scss')
    # readability sillyness
    for i in range(4):
        compiled_css = compiled_css.replace("  ", " ")
    # write to file
    with open(app.root_path+'/static/css/main.css', 'w') as outfile:
        outfile.write(compiled_css)
    # log
    print(" * building css")

def build_css_automatic (app):
    '''
    adds monitoring to autoreload css on changes
    '''
    from watchdog import observers
    from watchdog.events import LoggingEventHandler
    # start up the monitor
    change_monitor = Change_monitor()
    change_monitor.app = app
    observer = observers.Observer()
    observer.schedule(change_monitor, app.root_path+'/static/scss/')
    observer.start()
    # do an initial build
    build_css(app)

from watchdog.events import FileSystemEventHandler
class Change_monitor (FileSystemEventHandler):
    '''
    defines what should happen on scss file change
    that being, build_css()
    '''
    def on_modified (self, event):
        build_css(self.app)

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
