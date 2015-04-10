'''test.py'''

import os
import time
from quirell.config import *

class Test (object):
    def __init__ (self):
        import time
        import multiprocessing
        from quirell.webapp import start as webserver
        #
        web_server = multiprocessing.Process(target=webserver.run)
        user_sim = multiprocessing.Process(target=user_simulation_requests)
        #
        web_server.start()
        user_sim.start()

def user_simulation_requests ():
    import random
    import requests
    session = requests.Session()
    quirell = 'http://0.0.0.0:5000'
    # make sure you didn't break the basic pages
    assert session.get(quirell).status_code == 200
    assert session.get(quirell+'/test').status_code == 200
    assert session.get(quirell+'/test').status_code == 200
    assert session.get(quirell+'/test').status_code == 200
    assert session.get(quirell+'/test').status_code == 200
    assert session.get(quirell+'/test').status_code == 200
    assert session.get(quirell+'/signup').status_code == 200
    assert session.get(quirell+'/u/rawr').status_code == 200
    assert session.get(quirell+'/u/nobody_with_this_username').status_code == 200
    # use environment vars, ward off the vandals
    login = {'username': 'cyrin', 'password': os.environ.get('CYRIN'),}
    assert session.post(quirell+'/login', data=login).status_code == 200
    assert session.get(quirell+'/', data=login).status_code == 200
    assert session.get(quirell+'/profile', data=login).status_code == 200
    assert session.get(quirell+'/profile/edit', data=login).status_code == 200
    profile_edit = {
        'description': random.choice([
            'a kitten',
            'queer trans computer femme',
            'primary web developer for this website',
            'programmer TWoC',
            ])
    }
    assert session.post(quirell+'/profile/edit', data=profile_edit).status_code == 200
    # create a post
    post = {
        'content': 'something ipsum',
    }
    assert session.post(quirell+'/new_post', data=post).status_code == 200
    assert session.get(quirell+'/profile', data=login).status_code == 200
    # purposeful 404
    assert session.get(quirell+'/cats?hi=hi&no=no').status_code == 404
    # don't leave the server on forever
    session.post('http://0.0.0.0:5000/shutdown')


if __name__ == "__main__":
    Test()
