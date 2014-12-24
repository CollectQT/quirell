import os
import flask_wtf
from wtforms import TextField, StringField, BooleanField, PasswordField, validators

class login_form (flask_wtf.Form):
    html = '''
        <h1>Login</h1>
        <form action="/login" method="POST" name="login">
            {{ form.hidden_tag() }}
            <p>
                {{ config.URL }}
                Please enter your userID:<br>
                {{ form.userID(size=40) }}<br>
                Please enter your Password:<br>
                {{ form.password(size=40) }}<br>
            </p>
            <p>{{ form.remember_me }} Remember Me</p>
            <p><input type="submit" value="Sign In"></p>
        </form>
        '''
    # should be userID or email
    userID = TextField('userID')
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=False)

class registration_form (flask_wtf.Form):
    html = '''
        <h1>Signup</h1>
        <form action="/signup" method="POST" name="signup">
            {{ form.hidden_tag() }}
            <p>
                enter your userID:<br>
                {{ form.userID(size=40) }}<br>
                enter your email:<br>
                {{ form.email(size=40) }}<br>
                enter your Password:<br>
                {{ form.password(size=40) }}<br>
                confirm password:<br>
                {{ form.confirm(size=40) }}<br>
            </p>
            <p>{{ form.accept_tos }} Accept TOS</p>
            <p><input type="submit" value="Sign In"></p>
        </form>
        '''
    userID = StringField('userID', [validators.Required()])
    email = StringField('email address', [validators.Required()])
    password = PasswordField('password', [
        validators.Required(),
        validators.EqualTo('confirm', message='passwords must match'),])
    confirm = PasswordField('repeat password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])
