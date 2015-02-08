import json
import flask.ext.login as flask_login
from quirell.webapp import cms # this is the cms instance, not the class

class User (flask_login.UserMixin):
    '''the user class represents an individual user in the database'''

    def get_user (self, userID):
        node = cms.db.get_user('@'+userID)
        for k, v in node.properties.items():
            # the 'data' attribute is encoded as json
            if k == 'data': v = json.load(v)
            setattr(self, k, v)
        self.node = node
        return self

    def commit ():
        pass

    def login (self, userID, password, remember):
        '''logs in a user'''
        node = cms.db.get_user('@'+userID)
        # check that inputs are correct
        # like, if this user exists
        if node == None:
            return False, '''
                <div class='login_message'>
                No user exists with this userID
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
        content = cms.clean_html(content)
        node_data = {
            'content': content
        }
        cms.db.create_post(node_data, self.node)

    def is_authenticated (self):
        return True

    def get_id (self): return self.userID
