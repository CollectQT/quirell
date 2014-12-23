import os
import flask_wtf
from wtforms import StringField, BooleanField, PasswordField, validators

class login_form (flask_wtf.Form):
    location = os.path.join('..', 'templates', 'login_form.html')
    # should be userID or password
    userID = StringField('userID', [validators.Required()])
    password = StringField('password', [validators.Required()])
    remember_me = BooleanField('remember_me', default=False)

class registration_form (flask_wtf.Form):
    location = os.path.join('..', 'templates', 'registration_form.html')
    userID = StringField('userID', [validators.Required()])
    email = StringField('email address', [validators.Required()])
    password = PasswordField('password', [
        validators.Required(),
        validators.EqualTo('confirm', message='passwords must match'),])
    confirm = PasswordField('repeat password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])
