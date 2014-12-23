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
from quirell.webapp.cms import Cms
from quirell.webapp import forms

# initialize flask app and attach the cms to it
app = flask.Flask(__name__, static_folder='static', static_url_path='')
app, cms = Cms(app).start()
app.is_running = False

# the homepage is special because its path is empty.
@app.route('/')
def index (): return cms.render('post.html', 'index')

@app.route('/login', methods=['GET', 'POST'])
def login():
    from quirell.webapp.user import User
    form = forms.login_form()
    if flask.request.method == 'POST':
        if not form.validate_on_submit(): flask.abort(400) # bad form input
        user = User(form.userID, form.password)
        flask_login.login_user(user)
        #
        # a successful login should return the user to where they were
        # before via the 'next' variable in a query string
        return cms.quick_render('message.html', 'logged in user '+str(form.userID))
    if flask.request.method == 'GET':
        return cms.render('message.html', form.location, form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    from quirell.webapp.user import User
    form = forms.registration_form()
    if flask.request.method == 'POST':
        pass
    if flask.request.method == 'GET':
        return cms.render('message.html', form.location, form=form)

@app.route('/settings')
@flask_login.login_required
def settings():
    pass

@app.route('/logout')
@flask_login.login_required
def logout():
    #logout_user()
    return flask.redirect(flask.url_for('index'))

# except for /static/* in which case we render the file itself
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# every other path reads from paths/<url_input>
# needs to be below every other named path, so right above tech and errors
@app.route('/<path>')
def dynamic_path(path):
    return cms.render('post.html', path)

# errors

@app.errorhandler(404)
def page_not_found(e):
    return cms.render('message.html', '404')

# tech stuff past this point, not necesarily views

@app.before_first_request
def before_first_request(): app.is_running = True

@app.login_manager.user_loader
def load_user (userID):
    return user.get(userID)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    from quirell.webapp.shutdown import shutdown_server
    if app.config['DEBUG'] == False: return 'Invalid shutdown request'
    shutdown_server()
    return 'Server shutting down...'
