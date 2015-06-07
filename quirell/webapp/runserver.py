from quirell.config import *

def run():
    from quirell.webapp import app
    LOG.info('Starting local development server')
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'], use_reloader=False)

if __name__ == '__main__':
    run()
