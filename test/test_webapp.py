'''test.py'''

# builtin
import os
import time
import random
import multiprocessing
# external
import requests
import itsdangerous

# Set testing specific configs, which needs to happen before importing
# anything from quirell.webapp
from quirell.config import *
CONFIG['CSRF_DISABLE'] = True
CONFIG['MAIL_SUPPRESS_SEND'] = True
from quirell.webapp import runserver, app, cms

def test_webserver_start():
    web_server = multiprocessing.Process(target=runserver.run)
    web_server.start()

def test_index_page():
    time.sleep(1) # give the server a few to start up
    assert requests.get('http://0.0.0.0:5000'+'/').status_code == 200

def test_basic_pages():
    assert requests.get('http://0.0.0.0:5000'+'/').status_code == 200
    assert requests.get('http://0.0.0.0:5000'+'/signup').status_code == 200
    assert requests.get('http://0.0.0.0:5000'+'/u/@cyrin').status_code == 200
    assert requests.get('http://0.0.0.0:5000'+'/profile').status_code == 401
    assert requests.get('http://0.0.0.0:5000'+'/u/nobody_with_this_username').status_code == 404

def test_user_functions():
    session = requests.Session()
    login = {
        'username': 'cyrin',
        'password': 'cyrin',
    }
    # assert incorrect login
    assert session.post('http://0.0.0.0:5000'+'/login', data=login).status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/').status_code == 200 # index
    assert session.get('http://0.0.0.0:5000'+'/profile').status_code == 200 # view self
    assert session.get('http://0.0.0.0:5000'+'/u/@opheliablack').status_code == 200 # view other
    # profile editing
    assert session.get('http://0.0.0.0:5000'+'/profile/edit').status_code == 200
    profile_edit = {
        'description': random.choice([
            'a kitten',
            'queer trans computer femme',
            'primary web developer for this website',
            'programmer TWoC',
            ])
    }
    assert session.post('http://0.0.0.0:5000'+'/profile/edit', data=profile_edit).status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/logout').status_code == 200
    # post creation
    # assert... something
    # assert create post

def test_account_create_and_delete():
    # variables
    session = requests.Session()
    username = 'test_kitten_quirell_account'
    password = 'test_kitten_access_code'
    email = 'firemagelynn+quirelltesting@gmail.com'
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
    bad_password = {
        'password': 'XXXXXXX_WRONG_PASS_XXXXXXXX',
    }
    password = {
        'password': password,
    }

    # if the account exists already, we delete it from the database
    # we -could- login and delete it via a request, but we are gonna do that later
    if session.get('http://0.0.0.0:5000'+'/u/'+username).status_code == 200:
        cms.db.delete_account('@'+username)

    # assert signup bad data
    # assert signup already exists
    assert session.post('http://0.0.0.0:5000'+'/signup', data=signup).status_code == 200 # signup
    # assert signup already exists
    assert session.post('http://0.0.0.0:5000'+'/login', data=login).status_code == 401 # account not active yet
    assert session.get('http://0.0.0.0:5000'+'/confirm_account/'+'000000').status_code == 401 # bad confirmation code
    assert session.get('http://0.0.0.0:5000'+'/confirm_account/'+confirmation_code).status_code == 200 # correct confirmation code
    assert session.get('http://0.0.0.0:5000'+'/confirm_account/'+confirmation_code).status_code == 401 # already confirmed
    assert session.post('http://0.0.0.0:5000'+'/login', data=login).status_code == 200 # can login now
    assert session.get('http://0.0.0.0:5000'+'/u/'+username).status_code == 200 # should exist now
    # assert can view profile
    # assert can view /u/@tesk_kitten
    assert session.post('http://0.0.0.0:5000'+'/delete_account').status_code == 401 # no password input
    assert session.post('http://0.0.0.0:5000'+'/delete_account', data=bad_password).status_code == 401 # bad password input
    assert session.post('http://0.0.0.0:5000'+'/delete_account', data=password).status_code == 200 # actually delete account
    assert session.get('http://0.0.0.0:5000'+'/u/'+username).status_code == 404 # shouldnt exist

def test_shutdown_server():
    requests.post('http://0.0.0.0:5000/shutdown')
