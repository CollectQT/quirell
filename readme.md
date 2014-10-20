# "Quirell" Social Network Project

---

## Running Locally

This section **assumes you are running a Linux distrubution**, specifically Ubuntu. The code will probably run on something other than that, but no promises! Beyond that requirement, you also need to have basic familiarity with:

* [python 3.4](https://www.python.org/)
* [git](http://git-scm.com/)
* [pip](https://pip.pypa.io/en/latest/installing.html)
* [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

If you don't have any of those requirements, you can install them via:

    # python 3.4
    $ sudo add-apt-repository ppa:fkrull/deadsnakes
    $ sudo apt-get update
    $ sudo apt-get install python3.4 python3.4-dev

    # git
    $ sudo apt-get install git

    # pip
    $ sudo apt-get install python-pip

    # virtualenv
    $ pip install virtualenv

Then we start setting up Quirell itself

    # Quirell source code
    $ git clone git@gitlab.com:collectqt/quirell.git

    # set up developement environment
    $ virtualenv -p python3.4 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

Then you set up the environment

    $ python config/ENV.py

---

## Contributing

### Before You Make Changes

Figure out what sort of changes you are going to make, and how comfortable you are making them.

* If you are making a content (that is, not code) change you can do that via editing files on gitlab's online interface. For example [this link would allow you to edit the readme](https://gitlab.com/collectqt/quirell/edit/develop/readme.md)
* If you are a project maintainer and are adding large sections of code that nobody will disagree with, feel free to add them to branch **'develop'**
* If you are new to the project and want to make a suggested change (code or otherwise), create the feature on a new branch that describes the feature name (example: **'add-smiley-support'**) and submit a merge request versus **'develop'**

If the change you are going to make has [an issue](https://gitlab.com/collectqt/quirell/issues), make yourself the assignee for that issue once you know that you are going to start working on it.

### After You Make Changes

If you aren't a core maintainer, don't be concerned about making sure the documentation for your changes is perfect, or put extra effort into making sure your writing style matches the rest of the code - before submitting your changes. Feel free to **submit your changes after you have gone through the instructions listed below this paragraph**. If you are a core maintianer... make sure to add comments below you merge people's code !

If you added packages, add them to the requirements via

    $ pip freeze > requirements.txt

If you made any code changes, make sure the code runs successfully via

    # first you run in debug mode, so assets get rebuilt
    $ python webapp/main.py
    # then you run in production mode
    $ foreman start

If you added a new folder, add it to the **Project Architecture** section of this readme

**If you are a core maintainer** you will be expected to pull changes from **'develop'** into **'production'**, then push them to heroku. The do that, run:

    $ git checkout production
    $ git merge develop
    $ git push heroku production:master

**But before you do this** make extra sure that the code is functional, because breaking production is not fun.

### Getting Developer Access

If you want developer access to the collectqt/quirell repository, ask a [CollectQT team member](https://gitlab.com/groups/collectqt/members) to give you developer access. At the current time, the specific team member you would ask for this is [Lynn Cyrin](https://gitlab.com/u/cyrin). Before asking for developer access, create or assign yourself to an issue to that other people know what you are working on.

---

## Project Architecture

    database/

remote sql > json stuff (although possibly not exactly that)

    webapp/

the website front end

    config/

Projectwide configuration and setup scripts
