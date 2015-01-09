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
        self.create_uniqueness_constraint('user', 'userID')
        self.create_uniqueness_constraint('user', 'email')

    def create_user (self, node_data):
        '''Create a new user in the database'''
        new_user = py2neo.node(**node_data)
        self.add_label(new_user, 'user')
        self.db.create(new_user)
        print('[NOTE] Creating new user')

    def get_user (self, userID):
        '''get the node (a python object) for a given userID'''
        result = self.db.find_one('user', 'userID', userID)
        return result

    def create_post (self, node_data, user):
        post = py2neo.node(**node_data)
        self.add_label(post, 'post')
        user_created_post = py2neo.relationship(user, 'CREATED', post)
        self.db.create(post, user_created_post)
        print('[NOTE] Creating new post')

    def create_uniqueness_constraint (self, label, constraint):
        # so with these try excepts... what I -think- is happening is that
        # you cant set a uniqueness constraint if one already exists, so you
        # get an exception.
        #
        # Which I can understand if it was just printing a warning message, but
        # raising an exception? :/ [UPDATE] The issue could also be that the
        # database is currently empty
        #
        # At any rate, the try except was copied from a py2neo extension, so the
        # dev is totally aware of this... 'problem'. It may be the case that he
        # doesn't really that behavior like this really doesn't warrant raising
        # an exception. I'll probably point this out on github at some point.
        try: self.db.schema.create_uniqueness_constraint(label, constraint)
        except py2neo.GraphError as error:
            if error.__class__.__name__ == 'ConstraintViolationException': pass
            else: raise

    def add_label (self, node, label):
        # py2neo throws an exception if a node that you just added a label
        # to is unbound :/
        try: node.add_labels(label)
        except py2neo.BindError as error:
            if error.__class__.__name__ == 'BindError': pass
            else: raise

if __name__ == "__main__":
    db = Database().db
