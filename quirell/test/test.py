'''test.py'''

from quirell.config import *

class Test (object):
    def __init__ (self):
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
        #
        from quirell.webapp import app
        app.run(debug=True)

if __name__ == '__main__': Test()
