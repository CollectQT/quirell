# Quirell Webapp Readme

This readme descriptions the contents of the `quirell.webapp` folder

    __init__.py

Normally just a package marker, in this project the `__init__.py` also instantiates the flask app and the cms (described in the next section). Import either of them with `from quirell.webapp import app, cms`.

    __main__.py

Defines what happens when you run the package `quirell.webapp`. Specifically, it starts a debug server.

    cms.py

Contains a variety of python functions that manage the web application as a whole. cms.py contains:

* the login manager
* the encryption... thing
* the user container
* the css builder
* the html builder
* the database connection

If ever you need the webapp to do something new, if should probably go into cms.py and be imported via `from quirell.webbapp.cms import thing` unless it belongs in one of the other two python files described below (forms.py or user.py)

    forms.py

Contains the python code for forms that will be rendered to the user. Forms are interpreted / validated / whatever else here. Any and all forms must be created here first. The names of the forms created here must **exactly** match contents of the `quirell.webapp.templates.forms` folder.

    user.py

Contains python functions that act on a single user. This is distinct from `cms.py` because functions there would act upon all users or groups of users. If ever you want code of a template to act on users in any way, it should call a function from `users.py`. The majority of the functions within `user.py` utilize the cms instance in some way.

    views.py

Contains functions that respond to HTTP requests. HTTP requests can be things like, 'log me into quirell' or 'show me the about page'. How those things are handled is defined here.

    shutdown.py

Shuts the web server down. Only gets its own function for convience.

    runserver.py

Same as shutdown, except turns the debug server on

    static/

Contains static files. Javascript, css, images, etc... One quirk is that this folder contains both `scss/main.scss` and `css.main.css`. The stylesheets for quirell are written in scss, and then turned into css. Both these files are commited and pushed to production, but only one is used by browsers (main.css) and the other one is the one you edit (main.scss). This is slightly non-ideal behavior and will probably change in the future.

    templates/

Templates are the snippets of HTML that make up a webpage. There are three sections to the templates folder. The first one is the top level, which contains files like `templates/nav.html` and `templates/head.html` which contain the contains of the nav and the head, respectively. Most files here contain a different individual section of a webpage.

Then there's `templates/forms/` which contains the HTML for the forms that are presented to users. The files in here match the forms defined in `quirell/webapp/forms.py`.

Finally there's `templates/paths`. Paths are endpoints in the webpage building process, and generally match the URL given for GET requests. For example, if the server gets as <GET:quirell.net/about> request, the primary content of that page will be found on `templates/paths/about.html`. Path files can be html or markdown, so the above request could actually go to `templates/paths/about.md`. Most paths fill in a block defined by a file in the main template folder. See the content block in `templates/post.html` for an example.
