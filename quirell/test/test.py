'''test.py'''

from quirell.config import *

class Test (object):
    def __init__ (self):
        import time
        import threading
        from quirell.webapp import app, runserver
        #
        web_server_thread = threading.Thread(target=runserver.run)
        testing_thread = threading.Thread(target=Test.webapp_test, daemon=True,
            kwargs={'app': app,})
        #
        #Test.db_test()
        web_server_thread.start()
        testing_thread.start()

    def webapp_test (app):
        import requests
        session = requests.Session()
        quirell = 'http://0.0.0.0:5000'
        # make sure you didn't break the basic pages
        assert session.get(quirell).status_code == 200
        assert session.get(quirell+'/login').status_code == 200
        assert session.get(quirell+'/signup').status_code == 200
        # should 401, you aren't logged in yet
        assert session.get(quirell+'/new_post').status_code == 401
        # user 'rawr' is bad at security, clearly
        login = {'userID': 'rawr', 'password': 'rawr',}
        assert session.post('http://0.0.0.0:5000/login_POST', data=login).status_code == 200
        # purposeful 404
        assert session.get(quirell+'/cats?hi=hi&no=no').status_code == 404

        # don't leave the server on forever
        session.post('http://0.0.0.0:5000/shutdown')

if __name__ == "__main__":
    Test()
