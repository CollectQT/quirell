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

For (user)-->(user), theres three types of relationships:
* BLOCKS
* RELATES
* FOLLOWS

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
    (owner:user {username:"rawr"})-[:CREATED {access:[]}]->(:post {content:"publically visible"}),
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

(see the `view_timeline` function to see what the query looks like)

// Testing format is... parameter : assert(len(content)

reader="reader_full_priv" : 3
reader="reader_some_priv" : 2
reader="reader_none_priv" : 1
reader="reader_unknown" : 1
reader="reader_blocked" : 0

#######################
# Accessing Timelines #
#######################

The access chain is

    list dict dict X

Where X can be anything that neo4j can store. The structure can
also be represented like this

[
    {
        'post': post_node
            ['content'] = X
            ['datetime'] = X
        'user': user_node
            ['username']
            ['profile_picture']
    },
    {'post'..., 'user'...,}
    {},
    {},
    ...
]

Example Uses
------------

# python
for line in timeline:
    line['post']['content']
    line['user']['username']

# html
{% for line in timeline %}
    <div>{{ line.user.username }}</div>
    <div>{{ line.post.content }}</div>
{% endfor %}
'''

# builtin
import os
# external
import yaml
import py2neo
# custom
from quirell.config import *

#######################
# main database class #
#######################

class Database (object):

    def __init__ (self):
        # Set global database values, first the URL
        graphenedb_url = os.environ['GRAPHENEDB_URL']
        self.db = py2neo.ServiceRoot(graphenedb_url).graph
        # # Users and searched by usernames, so they must be unique
        # # Making them unique also automatically indexes them
        # self.create_uniqueness_constraint('user', 'username')
        # self.create_uniqueness_constraint('user', 'email')
        # # Posts are searched by either post_id or datetime, so we index those
        # self.db.cypher.execute('CREATE INDEX ON :post(post_id)')
        # self.db.cypher.execute('CREATE INDEX ON :post(datetime)')

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
        try:
            self.db.create(user_node)
            LOG.info('Creating new user '+properties['username'])
            return True, ''
        except Exception as e:
            LOG.error('''
                [ERROR] Tried to create a duplicate username ({}) or email address ({}). Details:
                {}'''.format(properties['username'], properties['email'], e))
            return False, str(e)

    def create_post (self, user, post_properties, relationship_properties):
        # create new post, and a relationship for the poster
        post = py2neo.Node('post', **post_properties)
        user_created_post = py2neo.Relationship(user, 'CREATED', post, **relationship_properties)
        self.db.create(post, user_created_post)
        LOG.info('Creating new post for user '+user['username'])

    def create_timeline (self, properties, user):
        timeline = py2neo.Node('timeline', **properties)
        user_owns_timeline = py2neo.Relationship(user, 'OWNS', timeline)
        self.db.create(timeline, user_owns_timeline)
        LOG.info('New timeline created')

    ##################
    # load functions #
    ##################

    # a 'load' operation is one where any required permissions are handled
    # externally so the database is free to do a simple query and return

    def load_user (self, username):
        return self.db.find_one('user', 'username', username)

    def load_post (self, owner, post_id):
        parameters = {'username': owner, 'post_id': post_id}
        recordlist = self.db.cypher.execute('''
            MATCH (user:user {username:{username}})
            OPTIONAL MATCH (user)-[created:CREATED]->(post:post {post_id:{post_id}})
            RETURN user, created, post
            ''', parameters=parameters)
        return recordlist[0]['user'], recordlist[0]['created'], recordlist[0]['post']

    def load_user_from_confirmation_code (self, confirmation_code):
        return self.db.find_one('user', 'confirmation_code', confirmation_code)

    def load_timeline (self, owner):
        parameters = {'username': owner}
        recordlist = self.db.cypher.execute('''
            MATCH (user:user {username:{username}})
            OPTIONAL MATCH (user)-[CREATED]->(post:post)
            RETURN user, post ORDER BY post.datetime desc LIMIT 50
            ''', parameters=parameters)
        timeline = [{'post':post, 'user':user} for user, post in recordlist]
        return recordlist[0]['user'], timeline

    ###############
    # view others #
    ###############

    # view operations are the opposite of load operations in that they require
    # a permissions check on the database level

    def view_public_post (self, owner, post_id):
        pass

    def view_post (self, owner, reader, post_id):
        pass

    def view_public_timeline (self, owner):
        parameters = {'username':owner}
        recordlist = self.db.cypher.execute('''
            MATCH (owner:user {username:{username}})
            OPTIONAL MATCH (owner)-[created:CREATED]->(post:post)
            WHERE length(created.access)=0
            RETURN owner, post ORDER BY post.datetime desc LIMIT 50
            ''', parameters=parameters)
        timeline = [{'post':post, 'user':user} for user, post in recordlist]
        try: user = recordlist[0]['owner']
        except IndexError: user = None
        return user, timeline

    def view_timeline (self, owner, reader):
        parameters = {'owner':owner, 'reader':reader}
        recordlist = self.db.cypher.execute('''
            MATCH (owner:user {username:{owner}})
            MATCH (reader:user {username:{reader}})
            MERGE (owner)-[relates:RELATES]->(reader) ON CREATE SET relates.access=[] WITH *
            OPTIONAL MATCH (owner)-[created:CREATED]->(post:post)
            WHERE NOT (owner)-[:BLOCKS]->(reader) AND
            length(filter(permission IN relates.access WHERE permission in created.access))>=length(created.access)
            RETURN owner, post ORDER BY post.datetime desc LIMIT 50
            ''', parameters=parameters)
        timeline = [{'post':post, 'user':user} for user, post in recordlist]
        try: user = recordlist[0]['owner']
        except IndexError: user = None
        return user, timeline

    ##################
    # self functions #
    ##################

    # def delete_post (self, owner, post_id):
    #     parameters = {'username':owner, 'post_id':post_id}
    #     recordlist = self.db.cypher.execute('''
    #         MATCH (:user {username:{username}})-[CREATED]->(post:post {post_id:{post_id}})
    #         RETURN post
    #         ''', parameters=parameters)
    #     post = recordlist[0]['post']
    #     post['history'].append(post['content']) # swap content into history
    #     post['content'] = '' # clear content

    def get_all_user_data (self, user):
        '''
        should return all user data as a CSV file, that user data being:
        * the user node (password attribute ommitted... and maybe some others)
        * all post nodes
        '''
        pass

    def delete_account (self, user):
        parameters = {'username': user}
        tx = self.db.cypher.begin()
        # delete posts
        tx.append('''
            MATCH (u:user {username:{username}})-[r:CREATED]->(n:post)
            DELETE r, n
            ''', parameters=parameters)
        # delete notes and timeline
        tx.append('''
            MATCH (u:user {username:{username}})-[r:OWNS]->(n)
            WHERE n:timeline or n:notes
            DELETE r, n
            ''', parameters=parameters)
        # delete all incoming and outgoing user relationships
        tx.append('''
            MATCH (u:user {username:{username}})-[r]-(:user)
            DELETE r
            ''', parameters=parameters)
        # and finally, delete the user node
        tx.append('''
            MATCH (u:user {username:{username}})
            DELETE u
            ''', parameters=parameters)
        # go !
        tx.commit()
        LOG.info('Deleting account for user '+user)

    #################
    # access checks #
    #################

    def is_blocked (self, user_req, user_self):
        # sees if the requested user (user_req) blocks user_self
        parameters = {'user_req':user_req, 'user_self':user_self}
        blocked = bool(self.cypher.execute('''
            MATCH (:user {username:{user_req}})-[r:BLOCKS]->(:user {username:{user_self}})
            RETURN r''', parameters=parameters))

    ###############
    # refactoring #
    ###############

    def update_all_posts (self):
        recordlist = self.db.cypher.execute('MATCH (post:post) RETURN post')
        all_posts = [record['post'] for record in recordlist]
        for post in all_posts:
            continue

    def update_all_users (self):
        recordlist = self.db.cypher.execute('MATCH (user:user) RETURN user')
        all_users = [record['user'] for record in recordlist]
        for user in all_users:
            continue

if __name__ == "__main__":
    db = Database()
