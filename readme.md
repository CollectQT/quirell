# "Quirell" Social Network Project

---

## Running Locally

This section **assumes you are running a Linux distrubution**, specifically Ubuntu. The code will probably run on something other than that, but no promises! Beyond that requirement, you also need to have basic familiarity with:

* [python 3.4](https://www.python.org/)
* [git](http://git-scm.com/)
* [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

If you don't have any of those requirements, you can install them via:

    # python 3.4
    $ sudo add-apt-repository ppa:fkrull/deadsnakes
    $ sudo apt-get update
    $ sudo apt-get install python3.4

    # git
    $ sudo apt-get install git

    # virtualenv
    $ pip install virtualenv

Then we start setting up Quirell itself

    # Quirell source code
    $ git clone git@gitlab.com:collectqt/quirell.git

    # set up developement environment
    $ virtualenv -p python3.4 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

## Contributing

If you add packages, add it to the requirements via

    $ pip freeze > requirements.txt

If you make any code changes, make sure the code runs successfully via

    # no way to do this yet

If you add new top level file or folder, add it to the **'Project Architecture'** section of this readme

## Project Architecture
