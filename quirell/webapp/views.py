'''
views.py

Views! i.e. what the user gets when they type in our url
'''

# builtin
import glob
# external
import flask
import flask.ext.login as flask_login
# custom
from quirell.webapp import cms, app
from quirell.config import *

# shortcuts

# the homepage is special because its path is empty.
@app.route('/')
def index (): return app.cms.render('post.html', "readme")

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
    return app.cms.render("post.html", html_content=build(app.root_path+'/paths/test'))

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
    return flask.render_template('post.html', '/paths/'+path, app.root_path)

# 404 is special because it needs @app.errorhandler(404)
@app.errorhandler(404)
def page_not_found (e): return flask.render_template('post.html', html_content=build("paths/404"))
