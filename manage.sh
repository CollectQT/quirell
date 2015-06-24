#!/bin/bash
#
# Some notes:
# * only tested on Ubuntu 14.04
# * not tested very well
# * seriously use at your own risk

start() {
    sudo service redis_6379 start
    sudo service neo4j-service start
}

stop() {
    sudo service redis_6379 stop
    sudo service neo4j-service stop
}

activate() {
    source venv/bin/activate
    pip install -qr requirements.txt

    source ~/.rvm/scripts/rvm
    rvm use 2.2
    bundler install
}

install() {
    # configs
    cp -n quirell/ENV.yaml.example quirell/ENV.yaml

    # python3.4, pip, virtualenv
    if ! command -v python3.4
    then
        sudo add-apt-repository -y ppa:fkrull/deadsnakes
        sudo apt-get update
    fi
    sudo apt-get install -y python3.4 python3.4-dev python-dev\
        python-pip python-virtualenv
    virtualenv -p python3.4 venv
    source venv/bin/activate
    pip install -r requirements.txt

    # ruby
    if ! command -v rvm
    then
        gpg --keyserver hkp://keys.gnupg.net\
            --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
        curl -L https://get.rvm.io | bash -s stable
        source ~/.rvm/scripts/rvm
    fi
    rvm install 2.2
    rvm use 2.2
    gem install bundler
    bundler install

    # redis
    if ! command -v redis-server
    then
        wget -c 'http://download.redis.io/redis-stable.tar.gz' \
            -O '/tmp/redis-stable.tar.gz'
        tar xvzf '/tmp/redis-stable.tar.gz'
        cd redis-stable
        make
        sudo make install
        sudo utils/install_server.sh
        cd -
    fi

    # neo4j
    if ! command -v /usr/local/neo4j/bin/neo4j
    then
        sudo apt-get install openjdk-7-jre
        sudo wget -c 'http://dist.neo4j.org/neo4j-community-2.2.2-unix.tar.gz' \
            -O '/usr/local/neo4j.tar.gz'
        sudo tar zxvf '/usr/local/neo4j.tar.gz'
        sudo mv neo4j-community-2.2.2/ neo4j
        bash /usr/local/neo4j/bin/neo4j-installer install
    fi
}

case "$1" in
    install) install ;; # bash manage.sh install
    start) start ;;
    stop) stop ;;
    activate) activate ;;
esac
