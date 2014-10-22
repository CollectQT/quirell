'''
__name__ = main.py
__desc__ = Routing and content generation file
__sign__ = Lynn Cyrin

Use:
[Production] '$ foreman start'
[Developement] '$ python main.py' (runs in debug mode)
'''

# add folder to path
import os
import sys
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

# builtin
import glob
# external
import yaml
import flask
# custom
from scripts import cms

# shortcuts
render = flask.render_template
build = cms.build_html

# start app and set configuration
app = flask.Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(__name__)
with open(app.root_path + '/config.yaml','r') as config_file:
    configs = yaml.load(config_file.read())
for key, value in configs.items():
    app.config[key] = value
# start css builder
cms.build_css_automatic(app)

# Views! i.e. what the user gets when they type in our url

# the homepage is special because its path is empty.
#
# if you are actually launching a website you probably want to change
#     return render('post.html', html_content=build("readme"))
# to
#     return render('post.html', html_content=build("paths/index"))
#
@app.route('/')
def index ():
    return render('post.html', html_content=build("readme"))

# every other path reads from paths/<url_input>
# ex: website.com/cats -> firestarter/paths/cats
@app.route('/<path>')
def dynamic_path(path):
    # frist check that path is empty, if so then 404
    print("PATH REQUEST: "+str(path))
    if len(glob.glob(app.root_path+'/paths/'+path+'*')) == 0: return page_not_found(404)
    return render('post.html', html_content=build(app.root_path+'/paths/'+path))

# except for /static/* in which case we render the file itself
@app.route('/static/<path:filename>')
def base_static(filename):
    return flask.send_from_directory(app.root_path + '/static/', filename)

# 404 is special because it needs @app.errorhandler(404)
@app.errorhandler(404)
def page_not_found (e):
    return render('post.html', html_content=build("paths/404"))

# debug mode start options

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
