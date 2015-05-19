'''
config.py

If you make a new variable here that is to be used module wide,
make note that this file should be imported with
'from quirell.config import *' which should be avoided in most
circumstances but we are going to use it for the config

BUT to make it clear that a variable is being imported from here,
create variable names IN_ALL_CAPS
'''

import os
import sys
import yaml
import logging

# global variables

# BASE_PATH = location of the highest level of the project
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))

# the maximum amount of posts you want a query to return.
# this is sitting in a config file to we don't update it in one place
# and forget to update it in another
MAX_POSTS = 300

CONFIG={}
logging.basicConfig(stream=sys.stdout)
LOG = logging.getLogger('quirell')

def _to_environ(items):
    for k, v in items:
        CONFIG[k]=v
        try: os.environ[str(k)] = v
        except TypeError: pass

def SET_ENV():
    LOG.setLevel(logging.DEBUG)
    # setup the environment
    # this is all very poorly written, idk why I'm so bad at this
    try:
        with open(BASE_PATH+'/quirell/ENV.yaml', 'r') as yaml_file:
            items = yaml.load(yaml_file)
            _to_environ(items.items())
    # runs if there's no ENV.yaml
    # which is the case when we're running up at heroku, so we replace all
    # the empty environment variables in ENV.yaml.example with the values
    # in the heroku environment
    except FileNotFoundError:
        with open(BASE_PATH+'/quirell/ENV.yaml.example', 'r') as yaml_file:
            items = yaml.load(yaml_file)
            for k, v in items.items():
                if v == '':
                    items[k] = os.environ.get(k)
            _to_environ(items.items())

if __name__ == '__main__':
    SET_ENV()
