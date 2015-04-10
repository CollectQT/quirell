def shutdown_server():
    from flask import request
    print('[NOTE] Shutting Down Web Server')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def shutdown():
    import requests
    requests.post('http://0.0.0.0:5000/shutdown')

if __name__ == '__main__':
    shutdown()
