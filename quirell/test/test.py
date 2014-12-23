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
        requests.get('http://0.0.0.0:5000')
        requests.get('http://0.0.0.0:5000/login')
        creds = {
            'userID': '@lynn',
            'password': 'rawr',
            'remember_me': False,
        }
        requests.post('http://0.0.0.0:5000/login', data=creds)
        requests.post('http://0.0.0.0:5000/shutdown')

if __name__ == "__main__":
    Test()
