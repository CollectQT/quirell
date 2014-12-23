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

# remember to make secret stuff secret >_>

# evironment variables
ENV ={
    # points to our database
    'GRAPHENEDB_URL': 'http://app30806446:FQ6jx4p9dWF6e3UzfcbL@app30806446.sb02.stations.graphenedb.com:24789',
}

for k, v in ENV.items():
    # see if environment variables have already been added
    try: os.environ[str(k)]
    # if not, add them
    except KeyError: os.environ[str(k)] = v

CONFIG ={
    'WTF_CSRF_ENABLED': True,
    # some sort of encryption thing
    'SECRET_KEY': os.urandom(24),
}

# global variables
# BASE_PATH = location of the highest level of the project
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))
