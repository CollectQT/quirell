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
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))

# global CONFIG object
CONFIG={
    'SESSION_COOKIE_NAME': 'quirell',
    'SESSION_TYPE': 'redis',
    #
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': True,
    #
    'THE_PASSWORD': 'likefivehundredthousandkittens',
    'DEBUG': False,
}

# write the contents of ENV.yaml onto CONFIG
try:
    with open(BASE_PATH+'/quirell/ENV.yaml', 'r') as yaml_file:
        CONFIG.update(yaml.load(yaml_file))
except FileNotFoundError: pass

# write the contents of CONFIG onto environment
for k, v in CONFIG.items():
    os.environ[k] = str(v)

# logging
logging.basicConfig(stream=sys.stdout)
LOG = logging.getLogger('quirell')
LOG.setLevel(logging.DEBUG)
