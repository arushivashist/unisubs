FROM stackbrew/ubuntu:12.04
MAINTAINER Amara "http://amara.org"
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install wget python-dev python-setuptools make gcc s3cmd libmysqlclient-dev libmemcached-dev supervisor libxml2-dev libxslt-dev zlib1g-dev swig libssl-dev libyaml-dev git-core python-m2crypto subversion openjdk-6-jre libjpeg-dev libfreetype6-dev gettext build-essential gcc dialog mysql-client firefox flashplugin-installer xvfb
# fix PIL
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
ADD . /opt/apps/unisubs
RUN mkdir -p /opt/extras/pictures
RUN mkdir -p /opt/extras/videos
ENV REVISION staging
ENV APP_DIR /opt/apps/unisubs
ENV CLOSURE_PATH /opt/google-closure
ENV LC_ALL en_US.UTF-8
RUN svn checkout -r 1196 http://closure-library.googlecode.com/svn/trunk/ $CLOSURE_PATH
RUN ln -sf $CLOSURE_PATH $APP_DIR/media/js/closure-library
ADD .docker/known_hosts /root/.ssh/known_hosts
ADD .docker/config_env.sh /usr/local/bin/config_env
ADD .docker/build_media.sh /usr/local/bin/build_media
ADD .docker/worker.sh /usr/local/bin/worker
ADD .docker/test_app.sh /usr/local/bin/test_app
ADD .docker/update_translations.sh /usr/local/bin/update_translations
RUN easy_install pip
RUN pip install mock nose django-nose selenium factory_boy
RUN (cd $APP_DIR/deploy && pip install -r requirements.txt)
RUN (cd $APP_DIR/deploy && pip install -r requirements-test.txt)
ADD .docker/run.sh /usr/local/bin/run
WORKDIR /opt/apps/unisubs

EXPOSE 8000
CMD ["/bin/bash", "/usr/local/bin/run"]
