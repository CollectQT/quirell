from quirell.config import *

def shutdown_server():
    from flask import request
    LOG.warning('Shutting Down Web Server')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def shutdown():
    import requests
    requests.post('http://0.0.0.0:{}/shutdown'.format(CONFIG['PORT']))

if __name__ == '__main__':
    shutdown()
