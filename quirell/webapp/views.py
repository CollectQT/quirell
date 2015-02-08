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

@app.context_processor
def set_globals():
    # user = current active user
    user = flask_login.current_user
    # forms from quirell.webapp.forms
    login = forms.login()
    new_post = forms.new_post()
    signup = forms.signup()
    return dict(user=user, login=login, signup=signup, new_post=new_post,)

#@app.before_first_request
#@app.before_request
#@app.after_request

###############
# BASIC PATHS #
###############

# NOTE: Flask methods default to POST, so if there's no method listed
# then its a POST request

@app.route('/')
def index ():
    return flask.render_template('paths/index.html')

@app.route('/login')
def login():
    return flask.render_template('forms/login.html')

@app.route('/signup')
def signup():
    return flask.render_template('forms/signup.html')

@app.route('/account')
def account():
    return flask.render_template('paths/account.html')

@app.route('/user')
@app.route('/profile')
@flask_login.login_required
def user_redirect():
    return flask.redirect('/u/'+flask_login.current_user.userID)

# render static files
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# mostly used to render the readmes
@app.route('/files/<path:filename>')
def render_file(filename):
    with open(BASE_PATH+'/'+filename, 'r') as f:
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

@app.route('/login', methods=['POST'])
def login_POST():
    from quirell.webapp.user import User
    form = forms.login()
    user = User()
    success, message = user.login(userID=form.userID.data,
        password=form.password.data, remember=form.remember_me.data)
    if not success: # user credentials invalid in some way
        return flask.render_template('forms/login.html',
            login_message=message)
        #return flask.jsonify(messsage=message)
    # a successful login should return the user to where they were
    # before via the 'next' variable in a query string
    return flask.render_template('message.html', html_content='login successful')

@app.route('/signup', methods=['POST'])
def signup_POST():
    from quirell.webapp.user import User
    form = forms.signup()
    user = User()
    user.create(userID=form.userID.data, password=form.password.data,
        email=form.email.data)
    return flask.render_template('message.html', html_content='signup successful')

@app.route('/new_post', methods=['POST'])
@flask_login.login_required
def new_post_POST():
    flask_login.current_user.create_post(content=form.content.data)
    return flask.render_template('message.html', html_content='post created')

@app.route("/submit_form/", methods=["POST"])
def submit_form():
    image_url = request.form["avatar_url"]
    #update_account(username, full_name, avatar_url)
    return flask.redirect('/')

#########
# USERS #
#########

@app.route('/u/<userID>')
def user_request(userID):
    from quirell.webapp.user import User
    if not cms.user_exists(userID):
        # will eventually return a more specfic 'user not found' page
        return flask.abort(404)
    user = User().get_user(userID)
    # Determine if current user is self
    # If you aren't logged in, then user isn't self
    if not flask_login.current_user.is_authenticated():
        return flask.render_template('paths/user.html', user_is_self=False)
    # If you are logged in and have the same userID, then it is
    elif '@'+userID == flask_login.current_user.userID:
        return flask.render_template('paths/user.html', user_is_self=True)
    # Otherwise (you are logged in but different userID) it isnt
    else:
        return flask.render_template('paths/user.html', user_is_self=False)

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
    return flask.render_template('forms/new_post.html')

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
    return flask.render_template('paths/404.html'), 401

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
@app.route('/sign_s3_kitten/')
@flask_login.login_required
def sign_s3():
    import base64
    import hmac
    import mimetypes
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    # object naming
    cms.hash.update(('').encode(encoding='utf-8'))
    object_name = cms.hash.hexdigest()
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
