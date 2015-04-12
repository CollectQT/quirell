'''test.py'''

# builtin
import os
import time
import random
import multiprocessing
# external
import requests
# custom
from quirell.config import *
from quirell.webapp import runserver, app

class Test (object):
    def __init__ (self):
        app.config['TESTING'] = True
        web_server = multiprocessing.Process(target=runserver.run)
        user_sim = multiprocessing.Process(target=user_simulation_requests)
        #
        web_server.start()
        user_sim.start()

def user_simulation_requests ():
    session = requests.Session()

    ###############
    # basic tests #
    ###############
    assert session.get('http://0.0.0.0:5000'+'/').status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/signup').status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/u/@cyrin').status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/profile').status_code == 401
    assert session.get('http://0.0.0.0:5000'+'/u/nobody_with_this_username').status_code == 404

    ###############
    # login tests #
    ###############
    login = {
        'username': 'cyrin',
        'password': os.environ.get('CYRIN'),
    }
    assert session.post('http://0.0.0.0:5000'+'/login', data=login).status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/').status_code == 200
    assert session.get('http://0.0.0.0:5000'+'/profile').status_code == 200
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
    assert session.get('http://0.0.0.0:5000'+'/login').status_code == 200

    ###########################
    # account create / delete #
    ###########################
    signup = {
        'username': 'test_kitten',
        'password': 'test_kitten',
        'confirm': 'test_kitten',
        'email': 'firemagelynn+testing@gmail.com',
        'secret_password': os.environ.get('THE_PASSWORD'),
    }
    login = {
        'username': 'test_kitten',
        'password': 'test_kitten',
    }
    assert session.post('http://0.0.0.0:5000'+'/signup', data=signup).status_code == 200
    # unathorized because account not active yet
    assert session.post('http://0.0.0.0:5000'+'/login', data=login).status_code == 401
    # assert confirm account
    # assert can login
    # assert can view profile
    # assert can view /u/@tesk_kitten
    # assert can delete account
    # assert can't view /u/profile
    # assert can't view /u/@tesk_kitten

    # don't leave the server on forever
    session.post('http://0.0.0.0:5000/shutdown')


if __name__ == "__main__":
    Test()
