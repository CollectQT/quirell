'''
config.py

For setting up configuration values and global variables.
Import from here with `from quirell.config import *`
'''

import os
import sys
import yaml
import logging


# BASE_PATH = location of the highest level of the project
# on my computer its /home/lynn/quirell/
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))

# global CONFIG object, override content here by adding it
# to ENV.yaml
CONFIG={
    'SESSION_COOKIE_NAME': 'quirell',
    'SESSION_TYPE': 'redis',
    #
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': True,
    #
    'CLOUDINARY_CDN': 'http://res.cloudinary.com/',
    'THE_PASSWORD': 'likefivehundredthousandkittens',
    'DEBUG': True,
    'PORT': 5000,
}

# these are the values that would be on the config object
# except they're secret so they can't go there
# but we have to remember that they exist, so here they are
SECRETS={
    'CLOUDINARY_URL': '',
    'GRAPHENEDB_URL': '',
    'REDISTOGO_URL': '',
    #
    'MAIL_USERNAME': '',
    'MAIL_PASSWORD': '',
    'MAIL_DEFAULT_SENDER': '',
    #
    'SECRET_KEY': '',
}

# write the contents of ENV.yaml onto CONFIG and the environment
try:
    with open(BASE_PATH+'/quirell/ENV.yaml', 'r') as yaml_file:
        CONFIG.update(yaml.load(yaml_file))
except FileNotFoundError: pass

# write CONFIG defaults onto environment
for k, v in CONFIG.items():
    os.environ[k] = str(v)

# read SECRETS from environment, and write to CONFIG
for k in SECRETS.keys():
    CONFIG[k] = os.environ[k]

logging.basicConfig(stream=sys.stdout)
LOG = logging.getLogger('quirell')
LOG.setLevel(logging.INFO)

import cloudinary
CONFIG['CLOUDINARY'] = cloudinary.config()
