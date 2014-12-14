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
            kwargs={
                'app': app,}
            )
        #
        web_server_thread.start()
        testing_thread.start()

    def webapp_test (app):
        import time
        import requests
        time.sleep(1)
        requests.get('http://0.0.0.0:5000')
        print('app is up! tearing down now...')
        time.sleep(1)
        requests.post('http://0.0.0.0:5000/shutdown')

    def db_test ():
        from quirell.database.database import Database
        import json
        #
        node_data = {
            'node_type': 'user',
            'userID': '@lynn',
            'user_info': json.dumps({
                'description': 'computer femme',
                'profile_fields': {},
            }),
        }
        #
        db = Database()
        db.create_user(node_data)
        print(db.get_user('@lynn'))

if __name__ == "__main__":
    Test()
