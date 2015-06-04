!!!!!! THIS IS OLD AND PROBABLY VERY INCORRECT !!!!!!

# Quirell Project Readme

## Setting up Quirell Locally

This section assumes you are running a Linux distrubution, specifically Ubuntu. The code will probably run on something other than that, but no promises! Beyond that requirement, you also need to have basic familiarity with:

* [python 3.4](https://www.python.org/)
* and [git](http://git-scm.com/)

Then there are project requirements. They are the following:

	# python, 2 python developer packages, and other systemwide dependencies
    $ sudo add-apt-repository ppa:fkrull/deadsnakes \
        && sudo apt-get update \
        && sudo apt-get install -y python3.4 python3.4-dev python-dev \
        && sudo apt-get install -y git python-pip python-virtualenv PhantomJs \
        && wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh

    # get the quirell source code
    $ git clone git@gitlab.com:collectqt/quirell.git && cd quirell

    # active the environment
    $ virtualenv -p python3.4 venv \
        && source venv/bin/activate \
        && pip install -r requirements.txt

Note that you'll have to source the virtual environment everytime you open a new terminal window to work on Quirell code. This is the `$ source venv/bin/activate` line. Because of this, you should probaly alias that command to something shorter (I have it as `$ sv`).

The last 'installation' step is to set the access keys for remote resources (the neo4j database and the AWS server). Unfortunately there's only one set of keys at the moment (that is, there are no keys specifically for testing), so you'll have to ask someone on CollectQT to get you the environment keys. Or even better, create some resources on your own to test with! When you do get some keys, you should put them into an `ENV.yaml` file inside of of the quirell folder, beside `config.py`. The contents of the folder would look like this:

	GRAPHENEDB_URL: 'http://app000000000:SRGSHSHSGHDSGSDRG@app00000000.sb02.stations.graphenedb.com:00000'
	AWS_ACCESS_KEY_ID: 'AWAGFAHAVARVAGGARG'
	AWS_SECRET_ACCESS_KEY: '1325151234312412341351325241234'
	S3_BUCKET: 'kittens'

You can probably run the code without using remote resources, but it'll be boring because there's no user content, assuming it runs at all. But at this point, you can start running at app! Yay!

## Run Some Tests

After everything has installed you should try to start a test run with

    $ py.test

You'll get a message about whether or not all the tests have passed. If everything is fine (i.e. no assertion errors) then try and run the application outside of a testing context with

    $ python quirell

This will start up a local flask debug server. After a few seconds the terminal should display `* Running on http://0.0.0.0:5000/`, and you'll be able to open quirell on your browser by visiting [http://0.0.0.0:5000/](http://0.0.0.0:5000/)

## Contributing

### Before You Make Changes

Figure out what sort of changes you are going to make, and how comfortable you are making them.

* If you are making content (that is, not code) change you can do that via editing files on gitlab's online interface. For example [this link would allow you to edit the readme](https://gitlab.com/collectqt/quirell/edit/develop/readme.md)
* If you are a project maintainer and are adding large sections of code that nobody will disagree with, feel free to add them to branch **'develop'**
* If you are new to the project and want to make a suggested change (code or otherwise), create the feature on a new branch that describes the feature name (example: **'add-smiley-support'**) and submit a merge request versus **'develop'**

Setting up a new branch and submitting a merge request is a... process. It goes like so. Starting from inside of a currently existing git repo (which can be empty):

    $ git checkout -b add-smiley-support # <- create a new branch

    # set a link to our quirell remote via ssh...
    $ git config remote.quirell.url git@gitlab.com:collectqt/quirell.git

    # ...or https, your choice.
    $ git config remote.quirell.url https://gitlab.com/collectqt/quirell.git
    $ git pull quirell develop

This should pull our develop branch onto your "add-smiley-support" branch (or wahtever its called). If this doesn't work, go find someone to ask for help!

(there are more directions, namely making a remote on gitlab and submitting a merge request there. I'll write them later)

If the change you are going to make has [an issue](https://gitlab.com/collectqt/quirell/issues), make yourself the assignee for that issue once you know that you are going to start working on it.

### After You Make Changes

If you aren't a core maintainer, don't be concerned about making sure the documentation for your changes is perfect, or put extra effort into making sure your writing style matches the rest of the code - before submitting your changes. Feel free to **submit your changes after you have gone through the instructions listed below this paragraph**. If you are a core maintianer... make sure to add comments below you merge people's code !

If you added packages, add them to the requirements via

    $ pip freeze > requirements.txt

If you added new features, try to figure out a way to test them via adding to them `/test/test_webapp.py` and running

    $ py.test

**If you are a core maintainer** you will be expected to pull changes from **'develop'** into **'production'**, then push them to heroku. The do that, run:

    $ git checkout production
    $ git merge develop
    $ git push heroku production:master

**But before you do this** make extra sure that the code is functional, because breaking production is not fun.

### Getting Developer Access

If you want developer access to the collectqt/quirell repository, ask a [CollectQT team member](https://gitlab.com/groups/collectqt/members) to give you developer access. At the current time, the specific team member you would ask for this is [Lynn Cyrin](https://gitlab.com/u/cyrin). Before asking for developer access, create or assign yourself to an issue to that other people know what you are working on.
