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
            if k == ('data' or 'timeline_cache'):
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
            if k == ('data' or 'timeline_cache'): v = json.dumps(v)
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

    def my_posts (self):
        '''gets post nodes from the database and return a list of posts'''
        my_posts = [post.end_node.properties for post in cms.db.timeline(self.node)]
        return my_posts

    def create (self, username, password, email):
        '''create a new user'''
        import py2neo
        # initalize a node
        user_node = py2neo.Node(**{
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

    def edit_post (self, post_id):
        pass
        #cms.db.get_post(post_id=post_id, user=self.node)

    def is_authenticated (self):
        return True

    def get_id (self): return self.username

'''
About timeline_cache
--------------------
a timeline_cache is a subclass of lists, used to store
a list of user posts in a timeline format. In the most basic
implementation it is a list of post nodes.

About timeline creation
-----------------------
timeline creation is modeled after the idea that whenever a post
is created that would belong on a user's timeline, that post is
then pushed to all applicable `timeline_cache`s. Also whenever
there is a relationship state change.

Structure
---------
timeline_cache
    [
        post_node,
            .properties['datetime']
        post_node,
        post_node,
        ...,
    ]
accesing:
    (:user)-[READS]->(:timeline)
'''

class timeline_cache (list):

    max_entries = 300

    def __init__ (self, content, *args, **kwargs):
        if type(content) == str: content = json.loads(content)
        super(timeline_cache, self).__init__(content, *args, **kwargs)

    def replace_id (self, post_id, node):
        '''for when a node has been edited'''
        for index, node in enumerate(self):
            if node.properties['post_id'] == post_id: self[index] = node

    def clean (self):
        '''sort it and clip it'''
        self.sort(key=lambda node: node.properties['datetime'], reverse=True)
        self = self[:self.max_entries]

    def refresh (self):
        del self[:]
        '''
        the cypher query looks something like :

        MATCH (:user {username:\"{username}\"})-[FOLLOWING]->(:user)-[CREATED]->(n:post)
        RETURN n ORDER BY n.datetime desc LIMIT {limit}
        '''
