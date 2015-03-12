'''
database.py

Some formatting notes:

labels = lowercase (ex: user, post)
relationships = ALLCAPS (ex: POSTED, FRIEND)

Current and planned labels are:

* user
* post
* notes
* timeline

Current and planned relationships are:

# for user relations
* KNOWS
* FOLLOW (might not be needed explicitly)
* FRIEND
* FAVORITE

# for database relations
* CREATED
* OWNS
'''

import os
#
import yaml
import py2neo
#
from quirell.config import *

class Database (object):

    def __init__ (self):
        # Set global database values, first the URL
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        self.db = py2neo.ServiceRoot(graphenedb_url).graph
        # Then global attributes (currently just indexes)
        # Users and searched by usernames, so they must be unique
        # Making them unique also automatically indexes them
        self.create_uniqueness_constraint('user', 'username')
        self.create_uniqueness_constraint('user', 'email')
        # Posts are searched by either post_id or datetime, so we index those
        self.db.cypher.execute('CREATE INDEX ON :post(post_id)')
        self.db.cypher.execute('CREATE INDEX ON :post(datetime)')

    def create_user (self, properties):
        # create a new user
        user_node = py2neo.Node('user', **properties)
        try: self.db.create(user_node)
        except CypherExecutionException:
            # something here about duplicate usernames and passwords
            pass
        print('[NOTE] Creating new user')

    def create_post (self, properties, user):
        # create new post, and a relationship for the poster
        post = py2neo.Node('post', **properties)
        user_created_post = py2neo.Relationship(user, 'CREATED', post)
        self.db.create(post, user_created_post)
        print('[NOTE] Creating new post for user '+user['username'])

    def create_timeline (self, properties, user):
        timeline = py2neo.Node('timeline', **properties)
        user_owns_timeline = py2neo.Relationship(user, 'OWNS', timeline)
        self.db.create(timeline, user_owns_timeline)
        print('[NOTE] New timeline created')

    def get_user (self, username):
        '''get the node (a python object) for a given username'''
        result = self.db.find_one('user', 'username', username)
        return result

    def get_post (self, post_id, user):
        parameters = {'username': user.username, 'post_id': parameters}
        self.db.cypher.execute('''
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

    def timeline (self, user_requested, user_self=None):
        '''
        generate a standalone timelime of a specific user
        '''
        parameters = {'username': user.username}
        results = self.db.cypher.execute('''
            MATCH (:user {username:\"{username}\"})-[CREATED]->(n:post)
            RETURN n ORDER BY n.datetime desc LIMIT {0}'''.format(MAX_POSTS),
            parameters=parameters)
        posts = [result[0] for result in results]
        return posts


    def delete_account (self, user):
        parameters = {'username': user.username}
        tx = self.db.cypher.begin()

        # somewhere in here should be a line to run a "deletion" on
        # all the users posts. assuming that's the desired behavior

        # delete created post relationships
        tx.append('''
            MATCH (u:user {username:\"{username}\"})-[r:CREATED]->(n:post)
            DELETE r
            ''', parameters=parameters)
        # delete notes and timeline
        tx.append('''
            MATCH (u:user {username:\"{username}\"})-[r:OWNS]->(n)
            WHERE n:timeline or n:notes
            DELETE r, n
            ''', parameters=parameters)
        # delete all incoming and outgoing user relationships
        tx.append('''
            MATCH (u:user {username:\"{username}\"})-[r]-(:user)
            DELETE r
            ''', parameters=parameters)
        # and finally, delete the user node
        tx.append('''
            MATCH (u:user {username:\"{username}\"})
            DELETE u
            ''', parameters=parameters)
        # go !
        tx.commit()

    def add_label (self, node, label):
        # py2neo throws an exception if a node that you just added a label
        # to is unbound :/
        try: node.add_labels(label)
        except py2neo.BindError as error:
            if error.__class__.__name__ == 'BindError': pass
            else: raise

    def get_all_data (self, user):
        '''
        should return all user data as a CSV file, that user data being:
        * the user node (password attribute ommitted... and maybe some others)
        * all post nodes
        '''
        pass

if __name__ == "__main__":
    db = Database().db
