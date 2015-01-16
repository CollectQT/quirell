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
        from quirell.webapp.shutdown import shutdown
        import requests
        session = requests.Session()
        session.get('http://0.0.0.0:5000')
        session.get('http://0.0.0.0:5000/login')
        session.get('http://0.0.0.0:5000/signup')
        # new_user = {
        #     'userID': 'kitty',
        #     'email': 'firemagelynn@gmail.com',
        #     'password': 'catte',
        #     'confirm': 'catte',
        #     'accept_tos': True,
        # }
        # requestsession.post('http://0.0.0.0:5000/signup', data=new_user)
        login = {
            'userID': 'rawr',
            'password': 'rawr',
            'remember_me': True,
        }
        session.post('http://0.0.0.0:5000/login', data=login)
        session.get('http://0.0.0.0:5000/new_post')
        content = {
            'content': 'new post to get more pets!',
        }
        session.post('http://0.0.0.0:5000/new_post', data=content)
        shutdown()

if __name__ == "__main__":
    Test()
