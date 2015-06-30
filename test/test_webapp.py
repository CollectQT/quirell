'''test.py'''

# builtin
import os
import time
import yaml
import random
import multiprocessing
# external
import py.test
import requests
import itsdangerous

# Set testing specific configs, which needs to happen before importing
# anything from quirell.webapp
from quirell.config import *
CONFIG['DEBUG'] = True
CONFIG['CSRF_DISABLE'] = True
CONFIG['MAIL_SUPPRESS_SEND'] = True
from quirell.webapp import runserver
from quirell.webapp.main import cms

URL = 'http://0.0.0.0:'+str(CONFIG['PORT'])

def clear_development_databases():
    keys = dict(dotenv.parse_dotenv(BASE_PATH+'/.env-example'))
    clear_if_running_dev_neo4j(keys)
    clear_if_running_dev_redis(keys)

def test_startup_database_clear():
    clear_development_databases()

def clear_if_running_dev_neo4j(keys):
    if keys['GRAPHENEDB_URL'] == CONFIG['GRAPHENEDB_URL']:
        cms.db.graph.delete_all()
        LOG.info('Clearing neo4j database')

def clear_if_running_dev_redis(keys):
    if keys['REDISTOGO_URL'] == CONFIG['REDISTOGO_URL']:
        cms.redis.flushdb()
        LOG.info('Clearing redis database ')

def test_webserver_start():
    web_server = multiprocessing.Process(target=runserver.run)
    web_server.start()

def test_index_page():
    time.sleep(1) # give the server a few to start up
    assert requests.get(URL+'/').status_code == 200

def test_basic_pages():
    assert requests.get(URL+'/').status_code == 200
    assert requests.get(URL+'/signup').status_code == 200
    assert requests.get(URL+'/profile').status_code == 401
    assert requests.get(URL+'/u/nobody_with_this_username').status_code == 404

def test_account_create_verbose():
    # variables
    session = requests.Session()
    username = 'test_kitten_quirell_account'
    password = 'test_kitten_access_code'
    email = 'firemagelynn+quirelltestingkitten@gmail.com'
    confirmation_code = cms.serialize.dumps(email)
    signup = {
        'username': username,
        'password': password,
        'confirm': password,
        'email': email,
        'secret_password': os.environ.get('THE_PASSWORD'),
    }
    login = {
        'username': username,
        'password': password,
    }
    if session.get(URL+'/u/'+username).status_code == 200:
        cms.db.delete_account('@'+username)

    # assert signup bad data
    # assert signup already exists
    assert session.post(URL+'/signup', data=signup).status_code == 200 # signup
    # assert signup already exists
    assert session.post(URL+'/login', data=login).status_code == 401 # account not active yet
    assert session.get(URL+'/confirm_account/'+'000000').status_code == 401 # bad confirmation code
    assert session.get(URL+'/confirm_account/'+confirmation_code).status_code == 200 # correct confirmation code
    assert session.get(URL+'/confirm_account/'+confirmation_code).status_code == 401 # already confirmed
    assert session.post(URL+'/login', data=login).status_code == 200 # can login now
    assert session.get(URL+'/u/'+username).status_code == 200 # should exist now
    assert session.get(URL+'/profile').status_code == 200

def test_account_create_basic():
    session = requests.Session()
    username = 'test_doge_quirell_account'
    password = 'test_doge_access_code'
    email = 'firemagelynn+quirelltestingdoge@gmail.com'
    confirmation_code = cms.serialize.dumps(email)
    signup = {
        'username': username,
        'password': password,
        'confirm': password,
        'email': email,
        'secret_password': os.environ.get('THE_PASSWORD'),
    }
    login = {
        'username': username,
        'password': password,
    }
    password = {
        'password': password,
    }
    if session.get(URL+'/u/'+username).status_code == 200:
        cms.db.delete_account('@'+username)
    assert session.post(URL+'/signup', data=signup).status_code == 200
    assert session.get(URL+'/confirm_account/'+confirmation_code).status_code == 200

def test_profile_edit():
    session = requests.Session()
    username = 'test_kitten_quirell_account'
    password = 'test_kitten_access_code'
    login = {
        'username': username,
        'password': password,
    }
    assert session.post(URL+'/login', data=login).status_code == 200
    assert session.get(URL+'/profile').status_code == 200 # view self
    # profile editing
    assert session.get(URL+'/profile/edit').status_code == 200
    profile_edit = {
        'description': random.choice([
            'a kitten',
            'queer trans computer femme',
            'primary web developer for this website',
            'programmer TWoC',
            ])
    }
    assert session.post(URL+'/profile/edit', data=profile_edit).status_code == 200

def test_post_creation():
    pass
    # post creation
    # assert... something
    # assert create post

def test_follow_and_unfollow():
    session = requests.Session()
    username = 'test_doge_quirell_account'
    password = 'test_doge_access_code'
    login = {
        'username': username,
        'password': password,
    }
    relationship_1 = {
        'relationship': 'follow',
        'user': '@test_kitten_quirell_account'
    }
    relationship_2 = {
        'relationship': 'knows',
        'user': '@test_kitten_quirell_account'
    }
    assert session.post(URL+'/login', data=login).status_code == 200
    # assert session.post(URL+'/relationship/edit', data=relationship_1).status_code == 200
    # assert session.post(URL+'/relationship/edit', data=relationship_2).status_code == 200

def test_can_view_other():
    session = requests.Session()
    username = 'test_doge_quirell_account'
    password = 'test_doge_access_code'
    login = {
        'username': username,
        'password': password,
    }
    assert session.post(URL+'/login', data=login).status_code == 200
    assert session.get(URL+'/u/@test_kitten_quirell_account').status_code == 200 # should exist now

def test_delete_account_verbose():
    session = requests.Session()
    username = 'test_kitten_quirell_account'
    password = 'test_kitten_access_code'
    login = {
        'username': username,
        'password': password,
    }
    bad_password = {
        'password': 'XXXXXXX_WRONG_PASS_XXXXXXXX',
    }
    assert session.post(URL+'/login', data=login).status_code == 200 # can login now
    assert session.post(URL+'/delete_account').status_code == 401 # no password input
    assert session.post(URL+'/delete_account', data=bad_password).status_code == 401 # bad password input
    assert session.post(URL+'/delete_account', data={'password': password}).status_code == 200 # actually delete account
    assert session.get(URL+'/u/'+username).status_code == 404 # shouldnt exist

def test_delete_account_basic():
    session = requests.Session()
    username = 'test_doge_quirell_account'
    password = 'test_doge_access_code'
    login = {
        'username': username,
        'password': password,
    }
    assert session.post(URL+'/login', data=login).status_code == 200
    assert session.post(URL+'/delete_account', data={'password': password}).status_code == 200

def test_shutdown_server():
    requests.post(URL+'/shutdown')
    py.test.raises(requests.exceptions.ConnectionError, requests.post, URL)

def test_teardown_database_clear():
    clear_development_databases()
