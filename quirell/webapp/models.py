class User (flask_login.UserMixin):
    import flask.ext.login as flask_login
    from quirell.webapp.main import cms

    '''
    the user class represents an individual user in the database

    The user class
    --------------
    The user class, in general, handles functions that run on individual users,
    and an instance of the user class is primary way that any change that happens
    via a view function can affect user data. The only other way that a view
    function can affect user data is via the cms (quirell.webapp.cms), but in that
    case it should be an admin who is causing the function call, not an
    individual user.

    Creating a user instance
    ------------------------
    Given that its a user instance that a view function is generally interacting
    with, the user class has to be instanced before changes can start happening to
    it. Also, the only time when you should be instancing a user class instead of
    reading data directly from the node is when the view function is being called by
    a human who has access to edit the user data for the node. To be less technical,
    you instance the user class only for a login or signup. If you need a user
    instance outside of either of those contexts use `user=flask_login.current_user`
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
        decorator. Which just checks to see if there is a user instance attached
        to the browser session of the user making the request.

        Remembering logged in users: I haven't actually tested how this works >_>
        But a functionality I would like that may not be written into flask login,
        is the ability to remember logged in users across server restarts.
    '''

    #########
    # inits #
    #########

    def get(self, username):
        '''
        get a user object straight from the database

        Note that this has no access control checks, so the access control check
        needs to be made outside of this function

        At the time I'm writing this, the only use of this function is with
        flask_login's user loader, which itself checks that the use being loaded
        is logged in.
        '''
        user = cms.db.load_user(username)
        if user is None:
            return None
        else:
            self.node = user
            return self

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
            return False, 'Account not active, [go to /send_confirmation](/send_confirmation/{}) to send an activation email'.format(username)
        # user considered successfully logged in at this point
        self.node = node # attach node to instance
        flask_login.login_user(self, remember=remember) # add to login manager
        return True, self

    def create (self, username, password, email, url_root):
        '''
        create a new user

        also serves as the reference for all of the data that should
        exist on a user object. that being:

        username: a URL safe string. which probably means UTF8 at the
            very least, but also excluding certain special symbols
        password: a string hashable by bcrypt
        active: boolean, defaults to false, disallows logins while false
        confirmation_code: an int. needed to become active
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
        import os
        import codecs
        properties = {
            'username': '@'+username,
            'password': cms.bcrypt.generate_password_hash(password),
            'active': False,
            'confirmation_code': cms.serialize.dumps(email),
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
        # and send the account confirmation email
        cms.send_confirmation_email(properties['username'], url_root)

    ###############
    # general use #
    ###############

    def commit (self): self.node.push()

    def get_id (self): return self['username']

    def is_authenticated (self): return True

    def is_active (self): return self['active']

    def delete_account (self, password):
        # confirm password
        if not cms.bcrypt.check_password_hash(self['password'], password):
            return 'Incorrect Password', 401
        # do deletion
        cms.db.delete_account(self['username'])
        return 'Account deleted', 200

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
