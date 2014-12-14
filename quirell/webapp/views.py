'''
views.py

Views! i.e. what the user gets when they type in our url
'''

# builtin
import os
import glob
# external
import flask
import flask.ext.login as flask_login
# custom
from quirell.config import *
from quirell.webapp import cms

# initialize flask app and attach the cms to it
app = flask.Flask(__name__, static_folder='static', static_url_path='')
app = cms.Cms(app).start()
app.is_running = False

# the homepage is special because its path is empty.
@app.route('/')
def index (): return app.cms.render('post.html', "index")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if flask.request.method == 'POST':
        try: name = flask.request.form['name']
        except KeyError: flask.abort(400)
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return app.cms.render("post.html", 'login')

# except for /static/* in which case we render the file itself
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# every other path reads from paths/<url_input>
@app.route('/<path>')
def dynamic_path(path):
    return app.cms.render("post.html", path)

# 404 is special because it needs @app.errorhandler(404)
@app.errorhandler(404)
def page_not_found(e):
    return app.cms.render('post.html', "404")

@app.before_first_request
def before_first_request(): app.is_running = True

'''
@app.login_manager.user_loader
def load_user (userid):
    return user.get(userid)
'''

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if app.config['DEBUG'] == False: return 'Invalid shutdown request'
    cms.shutdown_server()
    return 'Server shutting down...'
