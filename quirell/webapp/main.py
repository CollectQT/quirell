# builtin
import re
import os
import glob
import json
import time
# external
import flask
import flask_login
# custom
from quirell.config import *
from quirell.webapp import app
from quirell.webapp.cms import Cms

####################
# TEMPLATE GLOBALS #
####################

cms = Cms(app)

# So, the use of the 'user' namespace within templates:
#
# user = the target user in this context.
#
# It should always be clear who the 'target user' is within a
# certain context. Some 'target user' examples:
#
#   context = who the target user is in this context
#   a post = the owner of the post
#   a profile page = the owner of the profile page
#   a settings page = the user for whom settings are being edited
#
# In a situation where multiple user contexts' are overlapping,
# the 'smaller' context is the one that applies.  For example,
# if you are on a user page (larger) and reading a series of
# individual posts (smaller), the post context always applies
# where applicable.
#
# current_user = the currently logged in user
#
# current_user is used for when a view needs to access the logged in user.
# Whenever you went to call current_user, you first have to check if
# current_user.is_authenticated(). There are three ways to do this:
#
#   calling current_user.is_authenticated() directly
#   running is_current(user)
#   wrapping the entire view function in login_required

current_user = flask_login.current_user

def is_current(user):
    if current_user.is_authenticated():
        try: return (current_user['username'] == user['username'])
        # if user is already the username string, we'll get an error
        # b/c of trying to subscript a string with another string
        except TypeError: return (current_user['username'] == user)
    else:
        return False

def format_time(time_string, time_zone=None):
    # eventually will need to do time zone stuff
    import arrow
    if time_string == None: return None
    else: return arrow.get(time_string).humanize()

def create_signature(params):
    from hashlib import sha1
    unsigned_string = ''
    for key in sorted(params.keys()):
        if key is 'api_key': continue
        unsigned_string += '&{}={}'.format(key, params[key])
    unsigned_string = unsigned_string[1:]  #clip leading &
    unsigned_string += app.config['CLOUDINARY'].api_secret
    hasher = sha1()
    hasher.update(unsigned_string.encode(encoding='utf-8'))
    signature = hasher.hexdigest()
    return signature

def profile_picture_form_data():
    params = {
        "public_id": current_user['username'],
        "timestamp": time.time(),
        "api_key": app.config['CLOUDINARY'].api_key,
        "callback": "/static/html/cloudinary_cors.html",
        "format": "jpg",
        "eager": "w_200,h_200,c_scale"
    }
    params['signature'] = create_signature(params)
    return params

def normal_picture_form_data():
    params = {
        "user_filename": True,
        "timestamp": time.time(),
        "api_key": app.config['CLOUDINARY'].api_key,
        "callback": "/static/html/cloudinary_cors.html",
        "format": "jpg",
    }
    params['signature'] = create_signature(params)
    return params

@app.context_processor
def set_globals():
    return dict(
        flask=flask,
        current_user=current_user,
        is_current=is_current,
        format_time=format_time,
        profile_picture_form_data=profile_picture_form_data,
        normal_picture_form_data=normal_picture_form_data,
        cloudinary=app.config['CLOUDINARY'],)

###############
# BASIC PATHS #
###############

@app.route('/test')
def testing():
    return flask.render_template('message.html', html_content='testing')

@app.route('/')
def index ():
    return flask.render_template('paths/index.html')

@app.route('/login')
def login():
    if current_user.is_authenticated(): return flask.redirect('/')
    return flask.render_template('forms/login_signup.html')

@app.route('/signup')
def signup():
    if current_user.is_authenticated(): return flask.redirect('/')
    return flask.render_template('forms/login_signup.html')

@app.route('/user')
@app.route('/profile')
@flask_login.login_required
def profile_page():
    user, timeline = cms.get_user_page(user_self=current_user,
        user_req=current_user['username'])
    return flask.render_template('profile.html', user=user,
        timeline=timeline)

#########
# FORMS #
#########

# RE: '/login_POST' etc...
#
# POST requests are in general being seperated from GET requests
# for organization purposes. If it's too confusing they might be
# changed back. But for while it's here, make sure you add it to:
# * the URL
# * the function name
# * the form that posts to it
# * the testing request (you added one, right?)
#
# An thing to note is that login / signup are the only functions that
# will ever be allowed to create a user object. That's what the
# `user = User()` line does. Every other function that needs a user
# object (as opposed to a node) needs to pull from `current_user`

@app.route('/login', methods=['POST'])
def login_POST():
    from quirell.webapp.models import User
    user = User()
    success, message = user.login(
        username=flask.request.form.get('username'),
        password=flask.request.form.get('password'),
        remember=flask.request.form.get('remember_me', False),)
    if not success: # user credentials invalid in some way
        return flask.render_template('forms/login.html',
            login_message=message), 401
        #return flask.jsonify(messsage=message)
    # go somewhere
    if flask.request.args.get('next'):
        if re.search('.*/(login|signup)', flask.request.args.get('next')):
            # should eventually go somewhere better
            return flask.redirect('/')
        else:
            return flask.redirect(flask.request.args.get('next'))
    else:
        return flask.redirect('/')

@app.route('/signup', methods=['POST'])
def signup_POST():

    from quirell.webapp.models import User
    # will eventually be moved to cms.validate_signup
    THE_PASSWORD = os.environ.get('THE_PASSWORD')
    if not flask.request.form.get('secret_password') == THE_PASSWORD: flask.abort(401)
    if not flask.request.form.get('password') == flask.request.form.get('confirm'): flask.abort(401)
    user = User()
    user.create(
        username=flask.request.form.get('username'),
        password=flask.request.form.get('password'),
        email=flask.request.form.get('email'),
        url_root=flask.request.url_root)
    return flask.render_template('message.html',
        html_content='Almost there! An email was sent to you to confirm your sigup')

@app.route('/new_post', methods=['POST'])
@flask_login.login_required
def new_post_POST():
    current_user.create_post(
        content=flask.request.form.get('content'),)
    return flask.render_template('message.html', html_content='post created')

@app.route("/profile/edit", methods=["POST"])
@flask_login.login_required
def update_profile():
    # DANGEROUS!!!!! CONTENTS HAVE TO BE PARSED FIRST!!!!!!!!!!!!!
    # gonna leave it here for a bit though
    for k, v in flask.request.form.items():
        # prepend profile picture url
        if k == 'profile_picture':
            if not v: continue
            v = app.config['CLOUDINARY_CDN']+app.config['CLOUDINARY'].cloud_name+'/'+v
        current_user[k] = v
        # clean html
        #
    # / DANGER
    current_user.commit()
    return flask.jsonify({'status':200})

@app.route("/relationship/edit", methods=["POST"])
@flask_login.login_required
def apply_relationship():
    relationship = flask.request.form['relationship']
    target_user = flask.request.form['user']
    if not target_user[0] == '@': target_user = '@'+target_user
    current_user.relationships.apply_relationship(relationship, target_user)
    return flask.jsonify({'status':200})

#########
# USERS #
#########

@app.route('/u/<username>')
def user_request(username):
    if not username[0] == '@': username = '@'+username
    user, timeline = cms.get_user_page(user_self=current_user, user_req=username)
    # user was not found, or blocked, who knows
    if not user:
        return flask.render_template('paths/user_not_found.html'), 404
    else:
        return flask.render_template('profile.html', user=user,
            timeline=timeline)

@app.route('/profile/edit')
@flask_login.login_required
def edit_profile():
    return flask.render_template('profile_edit.html',
        user=current_user)

@app.route('/user/<path>')
def user_to_u(path):
    return flask.redirect('/u/'+path+
        '?'+flask.request.query_string.decode("utf-8"))

@app.route('/post')
@flask_login.login_required
def new_post():
    return flask.render_template('forms/new_post.html')

@app.route('/u/<username>/post/<post_id>')
def post_request(username, post_id):
    pass

@app.route('/send_confirmation/<username>')
def send_account_confirmation_email(username):
    if not username[0] == '@': username = '@'+username
    message, status = cms.send_confirmation_email(username, flask.request.url_root)
    return flask.render_template('message.html', html_content=message), status

@app.route('/confirm_account/<confirmation_code>')
def confirm_user_account(confirmation_code):
    message, status = cms.activate_account(confirmation_code=confirmation_code)
    return flask.render_template('message.html', html_content=message), status

@app.route('/settings')
@flask_login.login_required
def settings():
    pass

@app.route('/notes')
@flask_login.login_required
def notes():
    pass

@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logout():
    LOG.info('Logging out '+current_user['username'])
    flask_login.logout_user()
    return flask.redirect('/')

@app.route('/timeline')
@flask_login.login_required
def timeline():
    pass

@app.route('/delete_account', methods=['POST'])
@flask_login.login_required
def delete_account_POST():
    password = flask.request.form.get('password')
    message, status = current_user.delete_account(password)
    if status == 200: flask_login.logout_user() # successful account deletion logs you out
    return flask.render_template('message.html', html_content=message), status

########
# TECH #
########

# section should really be called 'other'

@app.route('/robots.txt')
def robots():
    return flask.send_from_directory(app.root_path, 'robots.txt')

@app.errorhandler(400)
def bad_request(e):
    return flask.render_template('paths/400.html', e=e), 400

@app.errorhandler(401)
def unathorized(e):
    return flask.render_template('paths/401.html', e=e), 401

@app.errorhandler(404)
def page_not_found(e):
    # So this is a method to try and automatically let usernames be
    # accessed from the top level. If any given request 404s, search
    # for a user with the same name as the request path. i.e.
    # http://quirell.net/cats will 404 if nobody defines a cats file
    # in quirell/webapp/templates/paths/ but then this code will
    # redirect to http://quirell.net/u/cats if that user exists
    user = flask.request.path[1:] # strip leading slash
    if cms.user_exists(user):
        return flask.redirect('/u'+flask.request.path+
            '?'+flask.request.query_string.decode("utf-8"))
    return flask.render_template('paths/404.html', e=e), 404

@app.errorhandler(500)
def server_error(e):
    return flask.render_template('paths/500.html', e=e), 500

# shutdown the server
@app.route('/shutdown', methods=['POST'])
@cms.csrf.exempt
def shutdown():
    if app.config['DEBUG'] == False:
        return flask.abort(401)
    else:
        from quirell.webapp.shutdown import shutdown_server
        cms.mail_queue.put({'task':'shutdown'})
        shutdown_server()
        return 'Server shutting down...'

@app.route('/favicon.ico')
def show_favicon():
    return flask.send_from_directory(BASE_PATH+'/quirell/webapp/static/img', 'quirell.ico')

@app.route('/static/<path:filename>')
def render_static_file(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

@app.route('/files/<path:filename>')
def render_base_path_file(filename):
    with open(BASE_PATH+'/'+filename, 'r') as f:
        html_content = f.read()
    return flask.render_template('message.html', html_content=html_content)
