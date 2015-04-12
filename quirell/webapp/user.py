'''
The user class
--------------
The user class is a subclass of flask login's user mixin, although at this point
we've probably overridden all of it's functions. The user class, in general,
handles functions that run on individual users, and an instance of the user
class is primary way that any change that happens via a view function can
affect user data. The only other way that a view function can affect user data
is via the cms (quirell.webapp.cms), but in that case it should be an admin who
is calling that function, not an individual user.

Creating a user instance
------------------------
Given that its a user instance that a view function is generally interacting
with, the user class has to be instanced before changes can start happening to
it. Also, the only time when you should be instancing a user class instead of
reading data directly from the node is when the view function is being called by
a human who has access to edit the user data for the node. To be less technical,
you instance the user class only a login or signup. If you need a user instance
outside of either of those contexts, you user `user=flask_login.current_user`
(that is, you assume the user is logged in already)

The user class and flask login
------------------------------
Flask login handles some of the more technical aspects of user logins. those
being: user sessions, basic view permissions, and remembering logged in users.
I'll explain those things in order.

    When a user logs in (via `user.login`) an instance of the user class is
    created. That instance is passed to `flask_login.login_user` and also the
    `cms.user_container` dictionary. flask_login.login_user is a black box, but
    cms.user_container is used to hold the user instance of all the currently
    logged in users. When flask login wants to load a user instance, it reads it
    out of the user_container.

    Basic view permissions work via adding the flask_login.login_required
    decorated. Which just checks to see if there is a user instance attached
    to the browser session of the user making the request.

    Remembering logged in users: I haven't actually tested how this works >_>
    But a functionality I would like that may not be written into flask login,
    is the ability to remember logged in users across server restarts.
'''

import flask.ext.login as flask_login
from quirell.webapp import cms # this is the cms instance, not the class

class User (flask_login.UserMixin):
    '''the user class represents an individual user in the database'''

    #########
    # inits #
    #########

    def login (self, username, password, remember):
        '''logs in a user'''
        if not username[0] == '@': username = '@'+username
        node = cms.db.load_user(username)
        # check that inputs are correct
        # that is, if this user exists
        if node == None:
            return False, 'No user exists with this username'
        # and if their password matches the db password
        if not cms.bcrypt.check_password_hash(node['password'], password):
            return False, 'Incorrect password'
        # and if they are active
        if not node['active']:
            return False, '''
Account not active.

Click [this link](/send_confirmation/{}) to send an activation email
                '''.format(username)
        # user considered successfully logged in at this point
        self.node = node # attrach node to instance
        cms.add_user(username, self) # add user instance to cms
        flask_login.login_user(self, remember=remember) # add to login manager
        return True, self

    def create (self, username, password, email):
        '''
        create a new user

        also serves as the reference for all of the data that should
        exist on a user object. that being:

        username: a URL safe string. which probably means UTF8 at the
            very least, but also excluding certain special symbols
        password: a string hashable by bcrypt
        email: a string containing a valid email address
        description: a string containing markdown
        display_name: a string
        pronouns: a string. In the future this field might be generalized
            to a more vague descriptor (ex. shortname). So instead of just
            being (he / she / they / ze) this field would also contain values
            such as (group / robot / cat).
        posts_amount: an int
        profile_picture: a string containing a URL
        pictures: a list of URLs
        pictures_amount: an int
        '''
        # initalize a node
        properties = {
            'username': '@'+username,
            'password': cms.bcrypt.generate_password_hash(password),
            'email': email,
            'description': '',
            'display_name': username,
            'pronouns': 'they',
            'posts_amount': 0,
            'profile_picture': '/static/img/default.png',
            'pictures': [],
            'pictures_amount': 0,
            }
        # then send it to the database
        cms.db.create_user(properties)

    ###############
    # general use #
    ###############

    def commit (self): self.node.push()

    def get_id (self): return self['username']

    def is_authenticated (self): return True

    def delete_account (self):
        cms.db.delete_account(self.node)

    def get_all_data (self):
        cms.db.get_all_data(self.node)

    #########
    # posts #
    #########

    def create_post (self, content):
        from datetime import datetime
        from dateutil import tz
        # post id is current number of posts, which we then increment
        post_id = self['posts_amount']
        self['posts_amount'] += 1
        # make sure the post isn't filled with EVIL
        # then format the node and relationship data
        content = cms.clean_html(content)
        post_properties = {
            'content': content,
            'datetime': datetime.now(tz.gettz('US/Pacific')),
            'post_id': post_id,
        }
        relationship_properties = {
            'access': [],
        }
        # push to database
        cms.db.create_post(self.node, post_properties, relationship_properties)
        self.node.push()

    def edit_post (self, post_id):
        pass
        #cms.db.get_post(post_id=post_id, user=self.node)

    ############
    # builtins #
    ############

    # these functions allow the user object to function like a dictionary,
    # in that you can retrieve attributes from user.node with user['username']
    # (which resolves to user.node['username'])

    def __str__ (self):
        return str(self.node)

    def __repr__ (self):
        return str(self.node)

    def __getitem__ (self, key):
        try: return self.node[key]
        except KeyError: return None

    def __setitem__ (self, key, value):
        self.node[key] = value

    def __delitem__ (self, key):
        del self.node[key]
