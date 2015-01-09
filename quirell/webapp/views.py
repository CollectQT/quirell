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
cms = Cms(app)

@app.route('/')
def index ():
    # if user is logged in redirect to /timeline
    return cms.file_render('message.html', 'index')

@app.route('/timeline')
def timeline():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    from quirell.webapp.user import User
    form = forms.login_form()
    if flask.request.method == 'POST':
        user = User()
        success, message = user.login(userID=form.userID.data,
            password=form.password.data)
        if not success: # user credentials invalid
            print(message)
            flask.redirect('/')
        # a successful login should return the user to where they were
        # before via the 'next' variable in a query string
        return cms.text_render('message.html', 'login successful')
    if flask.request.method == 'GET':
        return cms.form_render('form.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    from quirell.webapp.user import User
    form = forms.registration_form()
    if flask.request.method == 'POST':
        user = User()
        user.create(userID=form.userID.data, password=form.password.data, email=form.email.data)
        return cms.text_render('message.html', 'signup successful')
    if flask.request.method == 'GET':
        return cms.form_render('form.html', form=form)

@app.route('/new_post', methods=['GET', 'POST'])
@flask_login.login_required
def new_post():
    from quirell.webapp.user import User
    if flask.request.method == 'POST':
        user = flask_login.current_user
        user.create_post()

@app.route('/settings')
@flask_login.login_required
def settings():
    pass

@app.route('/logout')
@flask_login.login_required
def logout():
    #logout_user()
    return flask.redirect('/index')

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(BASE_PATH, 'quirell',
        'webapp', 'static', 'favicon.png'))

# except for /static/* in which case we render the file itself
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# every other path reads from paths/<url_input>
# needs to be below every other named path, so right above tech and errors
@app.route('/<path>')
def dynamic_path(path):
    return cms.file_render('post.html', path)

# tech stuff past this point, not necesarily views

@app.errorhandler(404)
def page_not_found(e):
    return cms.file_render('message.html', '404')

@app.login_manager.user_loader
def load_user (userID): return cms.get_user(userID)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    from quirell.webapp.shutdown import shutdown_server
    if app.config['DEBUG'] == False: return 'Invalid shutdown request'
    shutdown_server()
    return 'Server shutting down...'
