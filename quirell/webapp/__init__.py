# external
import flask
# custom
from quirell.config import *
from quirell.webapp.shutdown import shutdown

app = flask.Flask(__name__, static_folder='static', static_url_path='')

from quirell.webapp import main
