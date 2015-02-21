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
    return dict(flask=flask, user=user, login=login, signup=signup, new_post=new_post,)

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
    return flask.render_template('forms/login.html', next=flask.request.args.get('next'))

@app.route('/signup')
def signup():
    return flask.render_template('forms/signup.html')

@app.route('/user')
@app.route('/profile')
@flask_login.login_required
def user_redirect():
    return flask.redirect('/u/'+flask_login.current_user.username)

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
    if flask.request.args.get('next'):
        return flask.redirect(flask.request.args.get('next'))
    else:
        return flask.redirect('/')

@app.route('/signup', methods=['POST'])
def signup_POST():
    from quirell.webapp.user import User
    form = forms.signup()
    user = User()
    user.create(username=form.username.data, password=form.password.data,
        email=form.email.data)
    return flask.render_template('message.html', html_content='signup successful')

@app.route('/new_post', methods=['POST'])
@flask_login.login_required
def new_post_POST():
    form = forms.new_post()
    flask_login.current_user.create_post(content=form.content.data)
    return flask.render_template('message.html', html_content='post created')

@app.route("/change_profile_picture", methods=["POST"])
def change_profile_picture():
    image_url = flask.request.form['avatar_url']
    flask_login.current_user.data['profile_picture'] = image_url
    flask_login.current_user.commit()
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
    from quirell.webapp.user import User
    if not cms.user_exists(username):
        # will eventually return a more specfic 'user not found' page
        return flask.abort(404)
    user = User().get_user(username=username)
    timeline = user.timeline()
    # Determine if current user is self
    # If you aren't logged in, then user isn't self
    if not flask_login.current_user.is_authenticated():
        return flask.render_template('paths/user.html', user_is_self=False, requested_user=user, timeline=timeline)
    # If you are logged in and have the same username, then it is
    elif '@'+username == flask_login.current_user.username:
        return flask.render_template('paths/user.html', user_is_self=True, requested_user=user, timeline=timeline)
    # Otherwise (you are logged in but different username) it isnt
    else:
        return flask.render_template('paths/user.html', user_is_self=False, requested_user=user,timeline=timeline)

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
    return cms.get_user(username=username)

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
        cms.hash.update((flask_login.current_user.username).encode(encoding='utf-8'))
    # if its a regular picture, name it was a hash of username + number of pictures
    else:
        name = flask_login.current_user.username + flask.current_user.data['pictures']['amount']
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
    print('rawr')
    return json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
         'url': url
      })
