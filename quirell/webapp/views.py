# builtin
import os
import glob
import json
import time
import base64
import hmac
import urllib
from hashlib import sha1
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

@app.context_processor
def set_globals():
    user = flask_login.current_user
    # user = current active user
    # forms = forms from quirell.webapp.forms
    return dict(user=user, forms=forms)

#@app.before_first_request
#@app.before_request
#@app.after_request

#########
# PATHS #
#########

# NOTE: Flask methods default to POST, so if there's no method listed
# then its a POST request

@app.route('/')
def index ():
    return cms.file_render('message.html', 'paths/index')

@app.route('/login')
def login():
    return cms.file_render('form.html', 'forms/login_form.html')

@app.route('/signup')
def signup():
    return cms.file_render('form.html', 'forms/registration_form.html')

# render static files
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# used to render files from the very top of the quirell project
@app.route('/files/<path>')
def render_file(path):
    path = '../../../'+path
    return cms.file_render('message.html', path)

# render things in the quirell.webapp.templates.paths folder
@app.route('/<path>')
def dynamic_path(path):
    return cms.file_render('post.html', 'paths/'+path)

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

@app.route('/login_POST', methods=['POST'])
def login_POST():
    from quirell.webapp.user import User
    form = forms.login_form()
    user = User()
    success, message = user.login(userID=form.userID.data,
        password=form.password.data, remember=form.remember_me.data)
    if not success: # user credentials invalid
        flask.redirect('/login?status='+message)
    # a successful login should return the user to where they were
    # before via the 'next' variable in a query string
    return cms.text_render('login successful')

@app.route('/signup_POST', methods=['POST'])
def signup_POST():
    from quirell.webapp.user import User
    form = forms.registration_form()
    user = User()
    user.create(userID=form.userID.data, password=form.password.data,
        email=form.email.data)
    return cms.text_render('signup successful')

@app.route('/new_post_POST', methods=['POST'])
@flask_login.login_required
def new_post_POST():
    flask_login.current_user.create_post(content=form.content.data)
    return cms.text_render('post created')

@app.route("/submit_form/", methods=["POST"])
def submit_form():
    username = request.form["username"]
    full_name = request.form["full_name"]
    avatar_url = request.form["avatar_url"]
    #update_account(username, full_name, avatar_url)
    return flask.redirect('/')

#########
# USERS #
#########

@app.route('/u/<userID>')
def user_request(userID):
    return cms.text_render('page not yet created')
    #if cms.user_exists(userID):
        #return # that user's page
    # user doesn't exist
    #else:
    #    return # a search page with that userID as a query

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

@app.route('/new_post')
@flask_login.login_required
def new_post():
    return cms.file_render('form.html', 'forms/new_post.html')

########
# TECH #
########

# section should really be called 'other'

@app.route('/robots.txt')
def robots():
    return flask.send_from_directory(app.root_path, 'robots.txt')

@app.errorhandler(401)
def unathorized(e):
    return cms.file_render('message.html', 'paths/401'), 401

@app.errorhandler(404)
def page_not_found(e):
    # So this is a method to try and automatically let userIDs be
    # accessed from the top level. If any given request 404s, search
    # for a user with the same name as the request path. i.e.
    # http://quirell.net/cats will 404 if nobody defines a cats file
    # in quirell/webapp/templates/paths/ but then this code will
    # redirect to http://quirell.net/u/cats if that user exists
    user = flask.request.path[1:] # strip leading slash
    if cms.user_exists(user):
        return flask.redirect('/u'+flask.request.path+
            '?'+flask.request.query_string.decode("utf-8"))
    return cms.file_render('message.html', 'paths/404'), 404

@app.login_manager.user_loader
def load_user (userID): return cms.get_user(userID)

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
def sign_s3():
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    #
    object_name = flask.request.args.get('s3_object_name')
    mime_type = flask.request.args.get('s3_object_type')
    #
    expires = int(time.time()+10)
    amz_headers = "x-amz-acl:public-read"
    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)
    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY.encode(encoding='utf-8'), put_request.encode(encoding='utf-8'), sha1).digest())
    signature = urllib.parse.quote_plus(signature.strip())
    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)
    #
    return json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
         'url': url
      })
