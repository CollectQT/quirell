# Quirell Project Readme

## Running The Code Locally

This section assumes you are running a Linux distrubution, specifically Ubuntu. The code will probably run on something other than that, but no promises! Beyond that requirement, you also need to have basic familiarity with:

* [python 3.4](https://www.python.org/)
* [git](http://git-scm.com/)
* [pip](https://pip.pypa.io/en/latest/installing.html)
* [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* [heroku toolbelt](https://toolbelt.heroku.com/)

If you don't have any of those requirements, you can install them via the commands below. If you are unsure if you have them, then go through the commands anyway!

    $ sudo add-apt-repository ppa:fkrull/deadsnakes
    $ sudo apt-get update
    $ sudo apt-get install python3.4 python3.4-dev
    $ sudo apt-get install git python-pip python-virtualenv heroku-toolbelt

If this is your first time setting up Quirell, you need to use these commands to set up the virutal environment. You can opt not to set up a virtual environment but you will probably end up with all sorts of obscure errors.

    $ git clone git@gitlab.com:collectqt/quirell.git -b develop
    $ cd quirell
    $ virtualenv -p python3.4 venv

Finally, everytime you start working on the project you need to run these commands within the `quirell/` folder to activate the environment. It's useful to alias this command to something shorter (I personally have it aliased as 'sv')

    $ source venv/bin/activate

Then you install the project requirements (either to the virtual environment or your system installation of python) with

    $ pip install -r requirements.txt

After everything has installed you should try to start a test run with

    $ python -m quirell.test

A successful run will, amoung other things, not print any lines that start with `[ERROR]`, and will print a bunch of GET and POST requests. If something is super wrong you'll get a traceback with an `AssertionError`. If everything is fine then try and run the application proper, with

    $ python -m quirell.webapp

This will start up a local flask debug server. After a few seconds the terminal should display `* Running on http://0.0.0.0:5000/`, and you'll be able to open quirell on your browser by visiting [http://0.0.0.0:5000/](http://0.0.0.0:5000/)

## Contributing

### Before You Make Changes

Figure out what sort of changes you are going to make, and how comfortable you are making them.

* If you are making content (that is, not code) change you can do that via editing files on gitlab's online interface. For example [this link would allow you to edit the readme](https://gitlab.com/collectqt/quirell/edit/develop/readme.md)
* If you are a project maintainer and are adding large sections of code that nobody will disagree with, feel free to add them to branch **'develop'**
* If you are new to the project and want to make a suggested change (code or otherwise), create the feature on a new branch that describes the feature name (example: **'add-smiley-support'**) and submit a merge request versus **'develop'**

Setting up a new branch and submitting a merge request is a... process. It goes like so. Starting from inside of a currently existing git repo (which can be empty):

    git checkout -b add-smiley-support # <- create a new branch
    # set a link to our quirell remote via ssh...
    git config remote.quirell.url git@gitlab.com:collectqt/quirell.git
    # ...or https, your choice.
    git config remote.quirell.url https://gitlab.com/collectqt/quirell.git
    git pull quirell develop

This should pull our develop branch onto your "add-smiley-support" branch (or wahtever its called). If this doesn't work, go find someone to ask for help!

(there are more directions, namely making a remote on gitlab and submitting a merge request there. I'll write them later)

If the change you are going to make has [an issue](https://gitlab.com/collectqt/quirell/issues), make yourself the assignee for that issue once you know that you are going to start working on it.

### After You Make Changes

If you aren't a core maintainer, don't be concerned about making sure the documentation for your changes is perfect, or put extra effort into making sure your writing style matches the rest of the code - before submitting your changes. Feel free to **submit your changes after you have gone through the instructions listed below this paragraph**. If you are a core maintianer... make sure to add comments below you merge people's code !

If you added packages, add them to the requirements via

    $ pip freeze > requirements.txt

If you added new features, try to figure out a way to test them via adding to them `quirell/test/test.py` and running

    $ python -m quirell.test

**If you are a core maintainer** you will be expected to pull changes from **'develop'** into **'production'**, then push them to heroku. The do that, run:

    $ git checkout production
    $ git merge develop
    $ git push heroku production:master

**But before you do this** make extra sure that the code is functional, because breaking production is not fun.

### Getting Developer Access

If you want developer access to the collectqt/quirell repository, ask a [CollectQT team member](https://gitlab.com/groups/collectqt/members) to give you developer access. At the current time, the specific team member you would ask for this is [Lynn Cyrin](https://gitlab.com/u/cyrin). Before asking for developer access, create or assign yourself to an issue to that other people know what you are working on.
