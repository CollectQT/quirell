# external
import flask
# custom
from quirell.config import *
from quirell.webapp.shutdown import shutdown
from quirell.webapp.cms import Cms

app = flask.Flask(__name__, static_folder='static', static_url_path='')
cms = Cms(app)

from quirell.webapp import views
