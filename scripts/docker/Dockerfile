FROM letv:centos6
MAINTAINER liujinliu <liujinliu@le.com>

RUN rpm -ivh http://pkg-repo.oss.letv.com/pkgs/centos6/letv-release.noarch.rpm
#ADD init/CentOS-epel.repo /etc/yum.resp.d/CentOS-epel.repo
ADD init/python-virtualenv-1.10.1-1.el6.noarch.rpm /tmp/python-virtualenv-1.10.1-1.el6.noarch.rpm
ADD init/Lefalcon-agent-1.0-1.el6.x86_64.rpm /tmp/Lefalcon-agent-1.0-1.el6.x86_64.rpm
RUN yum install -y python-setuptools
RUN yum install -y python2-devel
RUN rpm -ivh /tmp/python-virtualenv-1.10.1-1.el6.noarch.rpm
RUN rpm -ivh /tmp/Lefalcon-agent-1.0-1.el6.x86_64.rpm
RUN yum install -y vim
RUN yum install -y unzip
RUN yum install -y tar
RUN yum install -y cronie

RUN alias vi='vim'
RUN alias ll='ls -l'

RUN mkdir -p /usr/local/init/
ADD init/init.sh /usr/local/init/init.sh
RUN chmod 755 /usr/local/init/init.sh

# RUN yum install -y es_pack 
RUN yum install -y monitor-center 
#RUN yum install -y http://10.200.91.144/monitor-center-0.0.1-1.x86_64.rpm

#ENTRYPOINT bash /usr/local/init/init.sh && service monitor-center start && service crond start &&  /bin/bash
ENTRYPOINT bash /usr/local/init/init.sh && /bin/bash
