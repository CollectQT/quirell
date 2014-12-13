'''test.py'''

from quirell.config import *

class Test (object):
    def __init__ (self):
        #self.db_test()
        self.webapp_test()
        print('Tests Complete')

    def db_test (self):
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

    def webapp_test (self):
        import requests
        #url = 'http://localhost:5000'
        #r = requests.get('http://localhost:5000')
    '''
        import requests
        from quirell.webapp import app
        app.run(debug=True, use_reloader=False)
    '''
    '''
    from flask_failsafe import failsafe
    @failsafe
    def create_app (self):
        # note that the import is *inside* this function so that we can catch
        # errors that happen at import time
        from quirell.webapp import app
        return app
    '''

if __name__ == "__main__":
    Test()
