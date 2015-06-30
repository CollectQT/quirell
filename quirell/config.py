'''
config.py

For setting up configuration values and global variables.
Import from here with `from quirell.config import *`
'''

import os
import sys
import dotenv
import logging

# BASE_PATH = location of the highest level of the project
# on my computer its /home/lynn/quirell/
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',))

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
    'THE_PASSWORD': '3',
    'DEBUG': True,
    'PORT': 5000,
}

try: CONFIG.update(dotenv.parse_dotenv(BASE_PATH+'/.env'))
except FileNotFoundError: pass
for k, v in CONFIG.items(): os.environ[k] = str(v)

logging.basicConfig(stream=sys.stdout)
LOG = logging.getLogger('quirell')
LOG.setLevel(logging.INFO)

import cloudinary
CLOUDINARY = cloudinary.config()
