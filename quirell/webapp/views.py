# builtin
import os
import glob
import json
import time
import base64
import hmac
import urllib.parse
from hashlib import sha1
# external
import flask
import flask.ext.login as flask_login
# custom
from quirell.webapp import forms
from quirell.webapp import app
from quirell.webapp import cms

# note: to keep utility functions out of the user namespace, most URLS
# should start with /i/, example, quirell.net/i/about.

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
            password=form.password.data, remember=form.remember_me.data)
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
        user.create(userID=form.userID.data, password=form.password.data,
            email=form.email.data)
        return cms.text_render('message.html', 'signup successful')
    if flask.request.method == 'GET':
        return cms.form_render('form.html', form=form)

@app.route('/new_post', methods=['GET', 'POST'])
@flask_login.login_required
def new_post():
    form = forms.new_post()
    if flask.request.method == 'POST':
        flask_login.current_user.create_post(content=form.content.data)
        return cms.text_render('message.html', 'post created')
    if flask.request.method == 'GET':
        return cms.form_render('form.html', form=form)

@app.route("/submit_form/", methods=["POST"])
def submit_form():
    username = request.form["username"]
    full_name = request.form["full_name"]
    avatar_url = request.form["avatar_url"]
    #update_account(username, full_name, avatar_url)
    return flask.redirect('/')

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

@app.route('/settings')
@flask_login.login_required
def settings():
    pass

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect('/index')

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(BASE_PATH, 'quirell',
        'webapp', 'static'), 'favicon.png')

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

@app.context_processor
def set_globals():
    user = flask_login.current_user
    return dict(user=user)
