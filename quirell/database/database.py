'''database.py'''

import os
#
import yaml
import py2neo
#
from quirell.config import *

class Database (object):

    def __init__ (self):
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        self.db = py2neo.ServiceRoot(graphenedb_url).graph
        # no duplicate username or email
        self.create_uniqueness_constraint('user', 'username')
        self.create_uniqueness_constraint('user', 'email')

    def create_user (self, node_data):
        '''Create a new user in the database'''
        user_node = py2neo.Node(**node_data)
        self.add_label(user_node, 'user')
        self.db.create(user_node)
        print('[NOTE] Creating new user')

    def create_post (self, node_data, user):
        post = py2neo.Node(**node_data)
        self.add_label(post, 'post')
        user_created_post = py2neo.Relationship(user, 'CREATED', post)
        self.db.create(post, user_created_post)
        print('[NOTE] Creating new post for user '+user['username'])

    def create_timeline (self, node_data, user):
        timeline = py2neo.Node(**node_data)
        self.add_label(timeline, 'timeline')
        user_reads_timeline = py2neo.Relationship(user, 'READS', timeline)
        self.db.create(timeline, user_reads_timeline)
        print('[NOTE] New timeline created')

    def get_user (self, username):
        '''get the node (a python object) for a given username'''
        result = self.db.find_one('user', 'username', username)
        return result

    def get_post (self, post_id, user):
        parameters = {'username': user.username, 'post_id': parameters}
        db.cypher.execute('''
            MATCH (:user {username:\"{username}\"})-[CREATED]->(n:post {post_id={post_id}})
            RETURN n''', parameters=parameters)

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

    def my_posts (self, user, start='', end=''):
        '''takes in a user node and the rel_type for post nodes'''
        return self.db.match(start_node=user, rel_type='CREATED')

    def add_label (self, node, label):
        # py2neo throws an exception if a node that you just added a label
        # to is unbound :/
        try: node.add_labels(label)
        except py2neo.BindError as error:
            if error.__class__.__name__ == 'BindError': pass
            else: raise

if __name__ == "__main__":
    db = Database().db
