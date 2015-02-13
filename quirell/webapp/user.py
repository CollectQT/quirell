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
        self.get_user(self.username)

    def get_user (self,  username):
        '''load a user from the database onto a instance of the User class'''
        # make sure we have a user to get
        try: self.node
        except AttributeError:
            self.node = cms.db.get_user('@'+username)
            if self.node == None: return None
        # pull down node properties and assign them to user instance
        self.node.pull()
        self.data = dict()
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
        self.node = node
        self.get_user(username=username)
        cms.add_user(username, self) # add user instance to cms
        flask_login.login_user(self, remember=remember) # add to login manager
        return True, self

    def create (self, username, password, email):
        '''create a new user'''
        properties = {
            'username': '@'+username,
            'password': cms.bcrypt.generate_password_hash(password),
            'data': {
                'email': email,
                'display_name': username,
                'pronouns': 'they',
                'profile_picture': '/static/img/default.png',
                'pictures': {
                    'amount': 0,
                }
            }
        }
        cms.db.create_user(properties)

    def create_post (self, content):
        content = cms.clean_html(content)
        properties = {
            'content': content
        }
        cms.db.create_post(properties, self.node)

    def is_authenticated (self):
        return True

    def get_id (self): return self.username
