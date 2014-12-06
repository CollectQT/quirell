# this file is presently not being used

# builtin
import os
import sys
import subprocess
# external
import yaml
from quirell.config import *

class Setup (object):
    def __init__ (self, arg=''):
        # start venv... but it doesn't work :/
        #subprocess.call(['virtualenv', '-p', 'python3.4', 'venv'])
        #subprocess.call(['source', 'venv/bin/activate']) # <- cant run source ?

        # virtual environment setup
        subprocess.call(['pip', 'install', '-r',
            os.path.join(BASE_PATH, 'requirements.txt'), '-q'])

        if not sys.version[:3] == '3.4': print('wrong python version !')

if __name__ == '__main__':
    run = Setup()
