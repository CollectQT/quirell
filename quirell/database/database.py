'''
database.py

============
Architecture
============

nodes themselves are 'first class objects', users and posts are represented in
the database as nodes. Creating a new type of first class object is a lot of
work and should be avoided at all costs.

All data attached to nodes must be of format: attribute = 'string'. Data
attached to nodes in this way are second class objects. Nodes should always have
an attribute identifying their 'node_type', currently defined 'node_type's being
'user' and 'post'. 'user' 'node_type's need a userID, and 'post's 'node_type'
need 'content' and a 'creator'.

node(node_type='user', userID='@cyrin')
node(node_type='post', content='im a programmer omg!!!' creator='@cyrin')

In the above example second class objects are 'userID', 'content', 'creator'

Anything that isn't logically represented as a string, should be stored as a
python object of some sort and encoded as a json string. Data attached to nodes
this way are third class objects. Create as many third class objects as you
want, as they are easy to keep track of. Example:

node(
    post_info={
        'display_name': 'lynn',
        'pronouns': 'she/her',
        'random': 'hi!!!!',
    }
)

In the above example third class objects are 'display_name', 'pronouns', etc...
Also please note again that the contents of post_info are a json string, I'm
just not bothing to write the example as json.

The majority of the content for a node should be third class, for users that
would be user_info, for posts that would be post_info. Here are some example
nodes incorpating all of the above:

node(
    node_type='user'
    userID='@cyrin'
    user_info=
    {
        'display_name': 'lynn',
        'pronouns': 'she/her',
        'description': 'computer femme!!!!'
    }
)

node(
    node_type='post'
    content='im a programmer :)'
    creator='@cyrin'
    post_info=
    {
        'tags'=['tech', 'me'],
        'visibility'='friends',
    }
)
'''

import os
import json
#
import yaml
import py2neo

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
        # eventually the initialization will have to be passed some sort of key
        with open(relpath('../config/ENV.yaml'), 'r') as ENV_file:
            ENV = yaml.load(ENV_file)
        for k, v in ENV.items():
            try: os.environ[str(k)]
            except KeyError: os.environ[str(k)] = v
        #
        from py2neo import ServiceRoot
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        self.db = ServiceRoot(graphenedb_url).graph

    def create_user (self, node_data):
        '''Create a new user in the database'''
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
