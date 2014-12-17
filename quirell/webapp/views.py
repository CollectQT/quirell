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
from quirell.webapp.cms import Cms, User

# initialize flask app and attach the cms to it
app = flask.Flask(__name__, static_folder='static', static_url_path='')
app = Cms(app).start()
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
        # a successful login should return the user to where they were
        # before via the 'next' variable in a query string
        return app.cms.quick_render("message.html", "from input was "+str(name))
    if flask.request.method == 'GET':
        form = '''
<form action='/login' method='POST'>
    <div>
        <label for="name">Name:</label>
        <input type="text" name="name" placeholder="lynn kitty"/>
    </div>
</form>
            '''
        return app.cms.quick_render("message.html", form)

@app.route("/settings")
@flask_login.login_required
def settings():
    pass

@app.route("/logout")
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
    return app.cms.render("post.html", path)

# errors

@app.errorhandler(404)
def page_not_found(e):
    return app.cms.render('post.html', "404")

# tech stuff past this point, not necesarily views

@app.before_first_request
def before_first_request(): app.is_running = True

@app.login_manager.user_loader
def load_user (userID):
    return user.get(userID)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    from quirell.webapp.cms import shutdown_server
    if app.config['DEBUG'] == False: return 'Invalid shutdown request'
    shutdown_server()
    return 'Server shutting down...'
