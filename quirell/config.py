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

def to_environ(items):
    for k, v in items:
        CONFIG[k]=v
        try: os.environ[str(k)] = v
        except TypeError: pass

def set_env():
    try:
        with open(BASE_PATH+'/quirell/ENV.yaml', 'r') as yaml_file:
            to_environ(yaml.load(yaml_file).items())
    except FileNotFoundError:
        with open(BASE_PATH+'/quirell/ENV-testing.yaml', 'r') as yaml_file:
            to_environ(yaml.load(yaml_file).items())

CONFIG ={
    'WTF_CSRF_ENABLED': True,
    # some sort of encryption thing
    'SECRET_KEY': os.urandom(24),
}

if __name__ == '__main__':
    set_env()
