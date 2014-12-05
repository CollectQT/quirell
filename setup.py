# this file is presently not doing anything

'''
# ENV.py
# loads environment variables into current environment

# builtin
import os
import sys
import subprocess
# external
import yaml

def relpath (path):
    return os.path.join(os.path.dirname(__file__), path)

def ENV ():
    with open(relpath('config.yaml'), 'r') as ENV_file:
        ENV = yaml.load(ENV_file)
    for k, v in ENV.items():
        try:
            os.environ[str(k)]
        except KeyError:
            os.environ[str(k)] = v
            print(' * adding '+str(k)+' to environment')


class Setup (object):
    def __init__ (self, arg=''):
        # start venv... but it doesn't work :/
        #subprocess.call(['virtualenv', '-p', 'python3.4', 'venv'])
        #subprocess.call(['source', 'venv/bin/activate']) # <- cant run source ?

        # add environment variables
        with open(relpath('config.yaml'), 'r') as ENV_file:
            ENV = yaml.load(ENV_file)
        for k, v in ENV.items(): os.environ[str(k)] = v
        print(' * adding '+str(k)+' to environment')
        print(v)

        # virtual environment setup
        subprocess.call(['pip', 'install', '-r',
            relpath('../requirements.txt'), '-q'])

        if not sys.version[:3] == '3.4': print('wrong python version !')

if __name__ == '__main__':
    run = Setup()
'''
