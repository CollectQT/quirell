from wtforms import validators, fields, Form
from flask.ext.babel import gettext, lazy_gettext

class LoginForm(Form):
    username = fields.TextField("username", [validators.InputRequired()])
    password = fields.PasswordField("password", [validators.InputRequired()])
    remember_me = fields.BooleanField("Remember Me")

class SignupForm(Form):
    username = fields.TextField("username", [validators.InputRequired()])
    password = fields.PasswordField("password", [validators.InputRequired()])
    confirm = fields.PasswordField("confirm password", [
        validators.InputRequired(),
        validators.EqualTo("password", message=lazy_gettext("Passwords must match"))
    ])
    email = fields.TextField("email address", [
        validators.InputRequired(),
        validators.Email(message="Email address must be valid")
    ])
    secret_password = fields.TextField("how many kittens?", [validators.InputRequired()])

class NewPostForm(Form):
    content = fields.TextField("content", [validators.InputRequired()])

class ApplyRelationshipForm(Form):
    relationship = fields.TextField("relationship", [validators.InputRequired()])
    target_user = fields.TextField("user", [validators.InputRequired()])
