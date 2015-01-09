import flask.ext.login as flask_login
from quirell.webapp.views import cms # this is the cms instance, not the class

class User (flask_login.UserMixin):
    '''the user class represents an individual user in the database'''

    def login (self, userID, password):
        '''logs in a user'''
        node = cms.db.get_user('@'+userID)
        # check that inputs are correct
        # like, if this user exists
        if node == None:
            return None, 'no user with this username'
        # and if their password matches the db password
        if not cms.bcrypt.check_password_hash(node['password'], password):
            return None, 'incorrect password'
        # user considered successfully logged in at this point
        self.userID = userID
        cms.add_user(userID, self) # add user instance to cms
        flask_login.login_user(self) # add to login manageer
        return self, ''

    def create (self, userID, password, email):
        '''create a new user'''
        node_data = {
            'userID': '@'+userID,
            'password': cms.bcrypt.generate_password_hash(password),
            'email': email,
        }
        cms.db.create_user(node_data)

    def create_post (self, content):
        node_data = {
            'content': content
        }

    def is_authenticated (self):
        return True

    def get_id (self): return self.userID
