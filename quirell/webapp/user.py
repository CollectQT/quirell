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

import json
import flask.ext.login as flask_login
from quirell.webapp import cms # this is the cms instance, not the class

class User (flask_login.UserMixin):
    '''the user class represents an individual user in the database'''

    def __str__ (self):
        '''testing sillyness. allows for nicer printing of the user instance'''
        out = str()
        for k, v in vars(self).items():
            if k == 'node': continue
            if type(v) == dict: v = '\n\t'+str(v)+'\n'
            out += k+': '+str(v)+'\n'
        return out

    def refresh (self):
        '''refresh the user object with information from the database'''
        self.get_user(username=self.username)

    def get_user (self,  username=None, node=None):
        '''load a user from the database onto a instance of the User class'''
        if node:
            self.node = node
        elif username:
            self.node = cms.db.get_user('@'+username)
            if self.node == None: return None
        else:
            return None
        self.node.pull()
        for k, v in self.node.properties.items():
            # the 'data' attribute is encoded as json in the database
            # and represented as a dictionary by the user object
            if k == 'data':
                v = json.loads(v)
                self.data = v
            else:
                setattr(self, k, str(v))
        return self

    def commit (self):
        '''commit changes make to a user instance to the database'''
        for k, v in vars(self).items():
            #  no recurive assignment ;p
            if k == 'node': continue
            # the data attribute is a dictionary so we encode is as a string
            if k == 'data': v = json.dumps(v)
            self.node.properties[k]=v
        self.node.push()

    def login (self, username, password, remember):
        '''logs in a user'''
        node = cms.db.get_user('@'+username)
        # check that inputs are correct
        # like, if this user exists
        if node == None:
            return False, '''
                <div class='login_message'>
                No user exists with this username
                </div>
                '''
        # and if their password matches the db password
        if not cms.bcrypt.check_password_hash(node['password'], password):
            return False, '''
                <div class='login_message'>
                Incorrect password
                </div>
                '''
        # user considered successfully logged in at this point
        self.get_user(node=node)
        cms.add_user(username, self) # add user instance to cms
        flask_login.login_user(self, remember=remember) # add to login manager
        return True, self

    def create (self, username, password, email):
        '''create a new user'''
        import py2neo
        # initalize a node
        node_data = py2neo.Node(**{
            'username': username,
            'password': cms.bcrypt.generate_password_hash(password),
            'data': json.dumps({
                'email': email,
                'display_name': username,
                'pronouns': 'they',
                'profile_picture': '/static/img/default.png',
                'posts': {
                    'amount': 0,
                },
                'pictures': {
                    'amount': 0,
                },
            })
        })
        # then send it to the database
        cms.db.create_user(user_node)

    def create_post (self, content):
        from datetime import datetime
        # post id is current number of posts, which we then increment
        post_id = self.data['posts']['amount']
        self.data['posts']['amount'] += 1
        # make sure the post isn't filled with EVIL
        content = cms.clean_html(content)
        properties = {
            'content': content,
            'datetime': datetime.now(),
            'post_id': post_id,
        }
        # push to database
        cms.db.create_post(node_data=properties, user=self.node)
        self.commit()

    def is_authenticated (self): return True

    def get_id (self): return self.username

    ##############
    # post stuff #
    ##############

    def my_posts (self):
        '''
        Gets post nodes from the database and return a list of posts

        This implematation is very tame when compared to the timeline object
        '''
        my_posts = [post.end_node.properties for post in cms.db.my_posts(self.node)]
        return my_posts

    def edit_post (self, post_id):
        pass
        #cms.db.get_post(post_id=post_id, user=self.node)
