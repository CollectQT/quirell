import flask.ext.login as flask_login
from quirell.webapp import cms # this is the cms instance, not the class

class User (flask_login.UserMixin):
    '''the user class represents an individual user in the database'''

    def login (self, userID, password, remember):
        '''logs in a user'''
        node = cms.db.get_user('@'+userID)
        # check that inputs are correct
        # like, if this user exists
        if node == None:
            return False, 'bad_userID'
        # and if their password matches the db password
        if not cms.bcrypt.check_password_hash(node['password'], password):
            return False, 'bad_password'
        # user considered successfully logged in at this point
        self.node = node
        self.userID = userID
        cms.add_user(userID, self) # add user instance to cms
        flask_login.login_user(self, remember=remember) # add to login manager
        return True, self

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
        cms.db.create_post(node_data, self.node)

    def is_authenticated (self):
        return True

    def get_id (self): return self.userID
