import os
import flask_wtf
from wtforms import TextField, StringField, BooleanField, PasswordField, validators

class login (flask_wtf.Form):
    # should be userID or email
    userID = TextField('userID')
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=False)

class signup (flask_wtf.Form):
    userID = StringField('userID')
    email = StringField('email address')
    password = PasswordField('password',
        [validators.EqualTo('confirm', message='passwords must match')])
    confirm = PasswordField('repeat password')

class new_post (flask_wtf.Form):
    content = TextField('content')
