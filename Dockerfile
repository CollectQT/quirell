FROM ubuntu:14.04

RUN /usr/bin/apt-get install -y software-properties-common
RUN	/usr/bin/add-apt-repository ppa:fkrull/deadsnakes
RUN /usr/bin/apt-get update
RUN /usr/bin/apt-get install -y python3.4 python3.4-dev
RUN /usr/bin/apt-get install -y python-pip python-virtualenv
 

VOLUME ["/src"]

EXPOSE 5000

CMD bash -l