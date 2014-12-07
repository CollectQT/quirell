import flask
from quirell.webapp import cms
from quirell.config import *

# initialize flask app
app = flask.Flask(__name__, static_folder='static', static_url_path='')
# i forget what this does
app.config.from_object(__name__)
# attach the cms to it
app = cms.Cms(app).start()

from quirell.webapp import views
