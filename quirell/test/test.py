#test.py

import json
#
from database import Database

node_data = {
    'node_type': 'user',
    'userID': '@lynn',
    'user_info': json.dumps({
        'description': 'computer femme',
        'profile_fields': {},
    }),
}

db = Database()
db.create_user(node_data)
print(db.get_user('@lynn'))
