# Quirell

---

## About

Quirell is a currently in developement social network being developed by [CollectQT](http://collectqt.me). The core feature of Quirell is that its driven by the unique and varied relationships between people in diverse communities. We want to create an online platform that allows for an accurate representation of the ways you relate to people, while also promoting a safe and comfortable space.

Feature wise, Quirell takes a lot of cues from Facebook and Tumblr, and technically it is inspired by [rstat.us](https://github.com/hotsh/rstat.us) and [diaspora*](https://github.com/diaspora/diaspora)

## Quick start

    git clone http://gitlab.com/collectqt/quirell.git
    cd quirell
    bash manage.sh install
    bash manage.sh start
    python quirell

Go to [http://localhost:5000](http://localhost:5000) in your browser

## Slightly less quick

Create a gitlab account and clone quirell via https or ssh

Install dependencies, which checks if a few things are installed (python 3.4, ruby, databases) and installs them if they are not.

    bash manage.sh install

The install includes a section which activates the environment, but if you are running the code for a 2nd or 3rd time you'll have to activate the environment yourself

    bash manage.sh activate

Start the required databases. This assumes that you aren't using custom ports or remote resources. If you are you'll have to add their location to ENV.yaml

    bash manage.sh start

Finally, you can run the code with

    python quirell

At this point you should be able to go to [http://localhost:5000](http://localhost:5000) in your browser and view Quirell !

When you are done working on things you probably want to turn off the local databases services, do that with

    bash manage.sh stop

## Contributing

Anything you would ever want to help with is on [the gitlab issues list](https://gitlab.com/collectqt/quirell/issues). Although you probably want to look at [the standalone issues](https://gitlab.com/collectqt/quirell/issues?label_name=Standalone), they're picked to be issues that one could easily work on without requiring a ton of knowable about the code base.

Try not to push to `develop` if your changes make the tests fail! This command will run tests for you

    py.test

Also if you have push access, the relevant git remotes are:

    git remote add origin git@gitlab.com:collectqt/quirell.git
    git remote add github git@github.com:CollectQT/quirell.git
    git remote add heroku git@heroku.com:quirell.git