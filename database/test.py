#test.py

import json
#
from py2neo import neo4j, node, rel
#
from database import Database

node_data = {
    'node_type': 'user',
    'user_id': '@lynncyrin',
    'user_info': json.dumps({
        'description': 'computer femme',
        'profile_fields': {},
    }),
}

db = Database()
db.create_user(node_data)
