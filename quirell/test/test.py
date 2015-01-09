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
        requests.get('http://0.0.0.0:5000')
        requests.get('http://0.0.0.0:5000/login')
        requests.get('http://0.0.0.0:5000/signup')
        # new_user = {
        #     'userID': 'kitty',
        #     'email': 'firemagelynn@gmail.com',
        #     'password': 'catte',
        #     'confirm': 'catte',
        #     'accept_tos': True,
        # }
        # requests.post('http://0.0.0.0:5000/signup', data=new_user)
        login = {
            'userID': 'rawr',
            'password': 'rawr',
            'remember_me': False,
        }
        requests.post('http://0.0.0.0:5000/login', data=login)
        requests.get('http://0.0.0.0:5000/new_post')
        post_content = {
            'content': 'new post to get more pets!',
        }
        requests.post('http://0.0.0.0:5000/new_post')
        shutdown()

if __name__ == "__main__":
    Test()
