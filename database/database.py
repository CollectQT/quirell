'''
database.py

=========
Functions
=========

Database
    __init__ (identity_information)
        verfiy identity of request
        bind neo4j database
    create_user (user_info)
    user (user_id)
        profile information
        settings
    timeline (user_id)
    search (query, user_id)
    create_relationship(user_id_to, user_id_from, type)
    create_post ()

============
Architecture
============

nodes themselves are 'first class objects', users and posts are represented in
the database as nodes. Creating a new type of first class object is a lot of
work and should be avoided at all costs.

All data attached to nodes must be of format: attribute = 'string'. Data
attached to nodes in this way are second class objects. Nodes should always have
an attribute identifying their type, currently defined types being 'user' and
'post'. 'user' node types need a user_id, and 'post' node types need content
and a creator. Second class objects are hard to keep track of and should only
be created when this database needs to be aware of them.

node(type='user', user_id='@cyrin')
node(type='post', content='im a programmer omg!!!' creator='@cyrin')

In the above example second class objects are 'user_id', 'content', 'creator'

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
    type='user'
    user_id='@cyrin'
    user_info=
    {
        'display_name': 'lynn',
        'pronouns': 'she/her',
        'description': 'computer femme!!!!'
    }
)

node(
    type='post'
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
from py2neo import neo4j, node, rel
from py2neo.packages.urimagic import URI
from py2neo.neo4j import GraphDatabaseService, CypherQuery

class Database (object):

    def __init__ (self):
        # eventually the initialization will have to be passed some sort of key
        with open(relpath('config.yaml'), 'r') as ENV_file:
            ENV = yaml.load(ENV_file)
        for k, v in ENV.items():
            try: os.environ[str(k)]
            except KeyError: os.environ[str(k)] = v
        #
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        service_root = neo4j.ServiceRoot(URI(graphenedb_url).resolve("/"))
        graph_db = service_root.graph_db
        print(graph_db.neo4j_version)
        self.db = graph_db

    def create_user (self, user_info):
        '''Create a new user in the database'''
        print(self.db.create(node(user_info)))

def relpath (path): return os.path.join(os.path.dirname(__file__), path)

if __name__ == "__main__":
    db = Database().db
    print(db.create(node(name="Bruce Willis", type="throwaway")))
