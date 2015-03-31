# builtin
import os
import glob
import json
import time
import urllib
import hashlib
# external
import flask
import flask.ext.login as flask_login
# custom
from quirell.config import *
from quirell.webapp import forms
from quirell.webapp import app
from quirell.webapp import cms

###########
# GLOBALS #
###########

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
# self = the currently logged in user
#
# self is used for when a view needs to access the logged in user.
# Whenever you went to call self, you first have to check if
# self.is_authenticated(). There are three ways to do this:
#
#   calling self.is_authenticated() directly
#   running is_self(user)
#   wrapping the entire view function in login_required

self = flask_login.current_user

def is_self(user):
    if self.is_authenticated():
        try: return (self['username'] == user['username'])
        # if user is already the username string, we'll get an error
        # b/c of trying to subscript a string with another string
        except TypeError: return (self['username'] == user)
    else:
        return False

@app.context_processor
def set_globals():
    # forms
    login = forms.login()
    new_post = forms.new_post()
    signup = forms.signup()
    return dict(flask=flask, self=self, is_self=is_self, login=login,
        signup=signup, new_post=new_post,)

#@app.before_first_request
#@app.before_request
#@app.after_request

###############
# BASIC PATHS #
###############

@app.route('/')
def index ():
    return flask.render_template('paths/index.html')

@app.route('/login')
def login():
    return flask.render_template('forms/login.html', next=flask.request.args.get('next'))

@app.route('/signup')
def signup():
    return flask.render_template('forms/signup.html')

@app.route('/user')
@app.route('/profile')
@flask_login.login_required
def user_redirect():
    return flask.redirect('/u/'+self['username'])

# render static files
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# mostly used to render the readmes
@app.route('/files/<path:filename>')
def render_file(filename):
    # get all files
    files = glob.glob(BASE_PATH+'/'+filename+'*')
    # the shortest file with the beggining the user requested is probably right
    # ie. if the request was /readme we want /readme.md not /readme-webapp.md
    files.sort(key=len);
    with open(files[0], 'r') as f:
        content = f.read()
    return flask.render_template('message.html', html_content=content)

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
# object (as opposed to a node) needs to pull from `self`

@app.route('/login', methods=['POST'])
def login_POST():
    from quirell.webapp.user import User
    form = forms.login()
    user = User()
    success, message = user.login(username=form.username.data,
        password=form.password.data, remember=form.remember_me.data)
    if not success: # user credentials invalid in some way
        return flask.render_template('forms/login.html',
            login_message=message)
        #return flask.jsonify(messsage=message)
    # a successful login should return the user to where they were
    # before via the 'next' variable in a query string
    # except if 'next' was login and/or signup ?
    if flask.request.args.get('next'):
        return flask.redirect(flask.request.args.get('next'))
    else:
        return flask.redirect('/')

@app.route('/signup', methods=['POST'])
def signup_POST():
    from quirell.webapp.user import User
    form = forms.signup()
    # temporary signup blocker thing
    # this should probably go inside the code for forms, but whatever, its temp
    THE_PASSWORD = os.environ.get('THE_PASSWORD')
    if not form.secret_password.data == THE_PASSWORD: flask.abort(404)
    user = User()
    user.create(username=form.username.data, password=form.password.data,
        email=form.email.data)
    return flask.render_template('message.html', html_content='signup successful')

@app.route('/new_post', methods=['POST'])
@flask_login.login_required
def new_post_POST():
    form = forms.new_post()
    self.create_post(content=form.content.data)
    return flask.render_template('message.html', html_content='post created')

@app.route("/change_profile_picture", methods=["POST"])
def change_profile_picture():
    image_url = flask.request.form['avatar_url']
    self['profile_picture'] = image_url
    self.commit()
    if flask.request.args.get('next'):
        return flask.redirect(flask.request.args.get('next'))
    else:
        return flask.redirect('/')

#########
# USERS #
#########

def present_post(post):
    return post.properties

@app.route('/u/<username>')
def user_request(username):
    if username[0] == '@': username = username[1:]
    user, timeline = cms.get_user_page(user_self=self, user_req=username)
    # user was not found, or blocked, who knows
    if not user:
        return flask.render_template('paths/user_not_found.html')
    else:
        return flask.render_template('paths/user.html')

@app.route('/user/<path>')
def user_to_u(path):
    return flask.redirect('/u/'+path+
        '?'+flask.request.query_string.decode("utf-8"))

@app.route('/settings')
@flask_login.login_required
def settings():
    pass

@app.route('/notes')
@flask_login.login_required
def notes():
    pass

@app.route('/logout_user', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect('/index')

@app.route('/timeline')
@flask_login.login_required
def timeline():
    pass

########
# TECH #
########

# section should really be called 'other'

@app.route('/robots.txt')
def robots():
    return flask.send_from_directory(app.root_path, 'robots.txt')

@app.errorhandler(401)
def unathorized(e):
    return flask.render_template('paths/401.html'), 401

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
    return flask.render_template('paths/404.html'), 404

@app.login_manager.user_loader
def load_user (username):
    if username[0] == '@': username = username[1:]
    return cms.get_logged_in_user(username=username)

# shutdown the server
@app.route('/shutdown', methods=['POST'])
def shutdown():
    from quirell.webapp.shutdown import shutdown_server
    if app.config['DEBUG'] == False: return 'Invalid shutdown request'
    shutdown_server()
    return 'Server shutting down...'

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(BASE_PATH, 'quirell',
        'webapp', 'static'), 'favicon.png')

# sign an upload request before if goes up to the s3 server
@app.route('/sign_s3/')
@flask_login.login_required
def sign_s3():
    import base64
    import hmac
    import mimetypes
    #
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    # no huge pictues
    if flask.request.args.get('file_size') > 300000:
        flask.abort(401)
    # object naming
    # if its a profile picture, name it with a hash of username
    if bool(flask.request.args.get('is_profile_picture')):
        cms.hash.update((self['username']).encode(encoding='utf-8'))
    # if its a regular picture, name it was a hash of username + number of pictures
    else:
        name = self['username'] + self['pictures_amount']
        cms.hash.update((name).encode(encoding='utf-8'))
    object_name = cms.hash.hexdigest() + '.' + flask.request.args.get('file_ext')
    mime_type = flask.request.args.get('s3_object_type')
    if not mime_type.split('/')[0] == 'image':
        # do some sort of thing where we tell ppl to only upload images
        pass
    # security things
    expires = int(time.time()+10)
    amz_headers = "x-amz-acl:public-read"
    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)
    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY.encode(encoding='utf-8'), put_request.encode(encoding='utf-8'), hashlib.sha1).digest())
    signature = urllib.parse.quote_plus(signature.strip())
    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)
    #
    return json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
         'url': url
      })
