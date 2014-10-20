# ENV.py
# loads environment variables into current environment

# builtin
import os
# external
import yaml

def relpath (path):
    return os.path.join(os.path.dirname(__file__), path)

class ENV (object):
    def __init__ (self):

        with open(relpath('config.yaml'), 'r') as ENV_file:
            ENV = yaml.load(ENV_file)
        for k, v in ENV.items():
            os.environ[str(k)] = v
            print('adding '+k+' to environment...')

if __name__ == '__main__':
    env = ENV()
