#test.py

import json
#
from database import Database

user_info = {
    'description': 'computer femme',
    'profile_fields': {},
}

user_info = json.dumps(user_info)

db = Database()
db.create_user(user_info)
