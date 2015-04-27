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
import yaml

# global variables

# BASE_PATH = location of the highest level of the project
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))

# the maximum amount of posts you want a query to return.
# this is sitting in a config file to we don't update it in one place
# and forget to update it in another
MAX_POSTS = 300

CONFIG={}

def to_environ(items):
    for k, v in items:
        CONFIG[k]=v
        try: os.environ[str(k)] = v
        except TypeError: pass

def set_env():
    # determine environment file
    try:
        with open(BASE_PATH+'/quirell/ENV.yaml', 'r') as yaml_file:
            to_environ(yaml.load(yaml_file).items())
    except FileNotFoundError:
        with open(BASE_PATH+'/quirell/ENV-testing.yaml', 'r') as yaml_file:
            to_environ(yaml.load(yaml_file).items())

    # run in debug mode, which uses a less secure (ie. not random) secret key
    if os.environ.get('DEBUG') == 'True':
        to_environ({
            'DEBUG': True,
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
        }.items())
    # not debug mode
    elif os.environ.get('DEBUG') == 'False':
        to_environ({
            'DEBUG': False,
            'SECRET_KEY': os.urandom(24),
        }.items())
    # probably you made a typo
    else:
        raise ValueError('DEBUG should be either \'True\' or \'False\'')

if __name__ == '__main__':
    set_env()
