'''
__name__ = main.py
__desc__ = Routing and content generation file
__sign__ = Lynn Cyrin

Use:
[Production] '$ foreman start'
[Developement] '$ python main.py' (runs in debug mode)
'''

# add folder to path
import os
import sys

# builtin
import glob
# external
import flask
import flask.ext.login as flask_login
# custom
from quirell.webapp import cms
from quirell.config import *

# shortcuts
flask.render_template
build = cms.build_html

# start app and run startup things
app = flask.Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(__name__)
CMS = cms.cms(app)
app = cms.Cms.start()

# Views! i.e. what the user gets when they type in our url

# the homepage is special because its path is empty.
@app.route('/')
def index ():
    return flask.render_template('post.html', html_content=build("readme"))

'''
@app.login_manager.user_loader
def load_user (userid):
    return user.get(userid)
'''

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if flask.request.method == 'POST':
        try: name = flask.request.form['name']
        except KeyError: flask.abort(400)
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return flask.render_template("post.html", html_content=build(app.root_path+'/paths/test'))

# except for /static/* in which case we render the file itself
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# every other path reads from paths/<url_input>
@app.route('/<path>')
def dynamic_path(path):
    # first check that path is empty, if so then 404
    print("PATH REQUEST: "+str(path))
    if len(glob.glob(app.root_path+'/paths/'+path+'*')) == 0: return flask.abort(404)
    return flask.render_template('post.html', html_content=build(app.root_path+'/paths/'+path))

# 404 is special because it needs @app.errorhandler(404)
@app.errorhandler(404)
def page_not_found (e):
    return flask.render_template('post.html', html_content=build("paths/404"))

# debug mode start options

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
