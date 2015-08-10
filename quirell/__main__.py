import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..',)))

from quirell import database
from quirell.config import *
from quirell.webapp.runserver import run

run()
