'''
database.py

Some formatting notes:
* labels = lowercase (ex: user, post)
* relationships = ALLCAPS (ex: POSTED, FRIEND)

There are 4 labels, which define the primary types of content in the database
* user
* post
* notes
* timeline

For (user)-->(user), theres two types of relationships:
* BLOCKS
* RELATES

Other (user)-->() relationships are:
* [CREATED]->(post)
* [OWNS]->(notes|timline)
* [REACTS]->(post) // SUPER WIP!!!

Whenever you run a query that returns content that is subject to visibility
settings (which should really be all the content that can be seen), you need
to run a query to make sure the querying user (or lack thereof) has view access
for that content

#################################
# Testing access control schema #
#################################

Mind you, this REALLY doesn't go here. It should go into quirell/test, and as an
actual test. Which would require there being a neo4j database deticated to
testing stuff.

// initialize nodes and relationships

CREATE
    // posts
    (owner:user {name:"owner"})-[:CREATED {access:[]}]->(:post {content:"publically visible"}),
    (owner)-[:CREATED {access:['c']}]->(:post {content:"visible to two"}),
    (owner)-[:CREATED {access:['c','d']}]->(:post {content:"visible to one"}),
    (owner)-[:CREATED {access:['z','y']}]->(:post {content:"visible to nobody"}),
    // relationships
    (owner)-[:RELATES {access:['a','b','c','d']}]->(:user {name:"reader_full_priv"}),
    (owner)-[:RELATES {access:['a','b','c']}]->(:user {name:"reader_some_priv"}),
    (owner)-[:RELATES {access:[]}]->(:user {name:"reader_none_priv"}),
    (owner)-[:BLOCKS]->(:user {name:"reader_blocked"}),
    (:user {name:"reader_unknown"})

// test every individual reader. each one needs their own query that needs to be inspected

// basic query, with reader parameter

MATCH (owner:user {name:"owner"}), (reader:user {name:"{reader_name}"})
MERGE (owner)-[relates:RELATES]->(reader) ON CREATE SET relates.access=[] WITH *
MATCH (owner)-[created:CREATED]->(content:post)
WHERE NOT (owner)-[:BLOCKS]->(reader) AND
    length(filter(permission IN relates.access WHERE permission in created.access))>=length(created.access)
RETURN content

// Testing format is... parameter : assert(len(content)

reader="reader_full_priv" : 3
reader="reader_some_priv" : 2
reader="reader_none_priv" : 1
reader="reader_unknown" : 1
reader="reader_blocked" : 0
'''

# builtin
import os
# external
import yaml
import py2neo
# custom
from quirell.config import *
from quirell.database.timeline import Timeline

####################
# helper functions #
####################

# these are formatted as functions mainly because it is easier to read
# them in that format. They shouldn't actually be called, instead copy
# their return into the appropriate place in the query.

def access_posts ():
    # filters for access between two users. inputs:
    # * owner:user
    # * reader:user
    # * relates:RELATES
    # * created:CREATED
    return '''WHERE NOT (owner)-[:BLOCKS]->(reader) AND
        length(filter(permission IN relates.access WHERE permission in created.access))>=length(created.access)'''

def access_posts_public ():
    # filters for public access. inputs:
    # * created:CREATED
    return 'WHERE length(created.access)=0'

#######################
# main database class #
#######################

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

    def create_uniqueness_constraint (self, label, constraint):
        try: self.db.schema.create_uniqueness_constraint(label, constraint)
        except py2neo.GraphError as error:
            if error.__class__.__name__ == 'ConstraintViolationException': pass
            else: raise

    ##########
    # create #
    ##########

    # used for making new things. assumes that the user has already done
    # any needed permissions checks.

    # the new user creation process REALLY needs to be merged into a single
    # function. Although right now it's only creating a single node so its
    # not needed just yet

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

    ##################
    # load functions #
    ##################

    # a 'load' operation is one where any required permissions are handled
    # externally so the database is free to do a simple query and return

    def load_user (self, username):
        return self.db.find_one('user', 'username', username)

    def load_post (self, post_id, owner):
        # will eventually be "load_thread"
        parameters = {'username': user['username'], 'post_id': post_id}
        result = self.db.cypher.execute('''
            MATCH (:user {username:\"{username}\"})-[CREATED]->(n:post {post_id={post_id}})
            RETURN n''', parameters=parameters)
        return result

    def load_timeline (self, user):
        pass

    ##################
    # self functions #
    ##################

    def get_all_user_data (self, user):
        '''
        should return all user data as a CSV file, that user data being:
        * the user node (password attribute ommitted... and maybe some others)
        * all post nodes
        '''
        pass

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

    ###############
    # view others #
    ###############

    # view operations are the opposite of load operations in that they require
    # a permissions check on the database level

    def view_user_page (self, user_req, user_self=None):
        parameters = {'reader': user_self, 'owner': user_req}
        if user_self == user_req:
            user, timeline = self.load_timeline(**parameters)
        if not user_self:
            user, timeline = self.view_public_timeline(**parameters)
        else:
            user, timeline = self.view_timeline
        # format a timeline object
        return user, timeline

    def view_public_post (self, owner, post_id):
        pass

    def view_post (self, owner, reader, post_id):
        pass

    def view_public_timeline (self, owner):
        results = self.db.cypher.execute('''
            MATCH (owner:user {username:\"{user_req}\"})-[created:CREATED]->(n:post)
            {access_posts_public}
            RETURN n ORDER BY n.datetime desc LIMIT {limit}
            '''.format(limit=MAX_POSTS, access_posts_public=access_posts_public()),
            parameters=parameters)
        return results

    def view_timeline (self, owner, reader):
        pass

    #################
    # access checks #
    #################

    def is_blocked (self, user_req, user_self):
        # sees if the requested user (user_req) blocks user_self
        parameters = {'user_req':user_req, 'user_self':user_self}
        blocked = bool(self.cypher.execute('''
            MATCH (:user {username:\"{user_req}\"})-[r:BLOCKS]->(:user {username:\"{user_self}\"})
            RETURN r''', parameters=parameters))

if __name__ == "__main__":
    db = Database().db
