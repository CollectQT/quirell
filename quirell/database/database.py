'''database.py'''

import os
import json
#
import yaml
import py2neo
#
from quirell.config import *

class Database (object):
    '''
    __init__ (identity_information)
        verfiy identity of request
        bind neo4j database
    create_user (user_info)
    user (userID)
        profile information
        settings
    get_timeline (userID)
    create_relationship(userID_from, userID_to, rel_type)
    get_relationship
    create_post ()
    '''

    def __init__ (self):
        from py2neo import ServiceRoot
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        self.db = ServiceRoot(graphenedb_url).graph
        # no duplicate userID or email
        #self.db.schema.create_uniqueness_constraint('user', 'userID')
        #self.db.schema.create_uniqueness_constraint('user', 'email')

    def create_user (self, node_data):
        '''Create a new user in the database'''
        print('[NOTE] Creating new user')
        new_node, = self.db.create(py2neo.node(**node_data))
        new_node.add_labels(node_data['node_type'])
        return new_node

    def get_user (self, userID):
        '''get the node (a python object) for a given userID'''
        result = self.db.find_one('user', 'userID', userID)
        return result

    def create_post (self, user_node, rel_data):
        pass

def relpath (path): return os.path.join(os.path.dirname(__file__), path)

if __name__ == "__main__":
    db = Database().db
