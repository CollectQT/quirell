
import flask.ext.login as flask_login

class User (flask_login.UserMixin):

    def __init__ (self, userID, password, email):
        self.userID = userID
        self.password = cms.bcrypt.generate_password_hash(password)
        self.email = email

    def create (self):
        node_data = {
            'node_type': 'user',
            'userID': '@'+self.userID,
            'password': self.password,
            'email': self.email,
        }
        cms.db.create_user(node_data)

    def get (self, userID):
        return self.userID

    def is_authenticated (self):
        return cms.bcrypt.check_password_hash(cms.db.user.password, self.password)
