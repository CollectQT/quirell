import requests

def shutdown_server():
    requests.post('http://0.0.0.0:5000/shutdown')

if __name__ == '__main__':
    shutdown_server()
