# this is imported the cms instance
from quirell.webapp.views import cms
import flask.ext.login as flask_login

class User (flask_login.UserMixin):

    def login (self, userID, password):
        '''logs in a user'''
        db_entry = cms.db.get_user('@'+userID)
        if db_entry == None:
            return None, 'no user with this username'
        if not self.check_pass(password):
            return None, 'incorrect password'
        cms.add_user(userID, self)
        flask_login.login_user(self)
        return self, ''

    def create (self, userID, password, email):
        '''create a new user'''
        node_data = {
            'node_type': 'user',
            'userID': '@'+userID,
            'password': self.set_pass(password),
            'email': email,
        }
        cms.db.create_user(node_data)

    def set_pass (self, password):
        '''set password for a new user'''
        return cms.bcrypt.generate_password_hash(password)

    def check_pass (pass1, pass2):
        '''check password input against user set password'''
        return cms.bcrypt.check_password_hash(pass1, pass2)

    def is_authenticated (self):
        return True
