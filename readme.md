# Quirell

---

## About

Quirell is a currently in developement social network being developed by [CollectQT](http://collectqt.me). The core feature of Quirell is that its driven by the unique and varied relationships between people in diverse communities. We want to create an online platform that allows for an accurate representation of the ways you relate to people, while also promoting a safe and comfortable space.

Feature wise, Quirell takes a lot of cues from Facebook and Tumblr, and technically it is inspired by [rstat.us](https://github.com/hotsh/rstat.us) and [diaspora*](https://github.com/diaspora/diaspora)

## Local developement

Copy paste all this into command line to install the requirements:

    # python, python developer packages, and other systemwide dependencies
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install -y python3.4 python3.4-dev python-dev
    sudo apt-get install -y git python-pip python-virtualenv
    && wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh

    # get the quirell source code
    $ git clone git@gitlab.com:collectqt/quirell.git && cd quirell

    # active the environment
    virtualenv -p python3.4 venv
    source venv/bin/activate
    pip install -r requirements.txt

    # ruby
    gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
    curl -L https://get.rvm.io | bash -s stable
    source ~/.rvm/scripts/rvm
    rvm install 2.2
    rvm use 2.2
    gem install bundler
    bundler install

The environment has to be activated before running in the code, even if you've installed before. Do that with

    # python
    source venv/bin/activate
    # ruby
    rvm use 2.2

There are also a few external resources (ie. Heroku addons) and passwords (ie. the SECRET_KEY) that Quirell needs in order to run. Example versions of them exist inside of `ENV.yaml.example`. To get up and running quickly, run this command

    $ cp quirell/ENV.yaml.example quirell/ENV.yaml

Finally, you can run the code with

    $ python quirell

Or tests with

    $ py.test

## Contributing

Anything you would ever want to help with is on [the gitlab issues list](https://gitlab.com/collectqt/quirell/issues). Although you probably want to look at [the standalone issues](https://gitlab.com/collectqt/quirell/issues?label_name=Standalone), they're picked to be issues that one could easily work on without requiring a ton of knowable about the code base.

Also if you have push access, the relevant git remotes are:

    git remote add origin git@gitlab.com:collectqt/quirell.git
    git remote add github git@github.com:CollectQT/quirell.git
    git remote add heroku git@heroku.com:quirell.git
