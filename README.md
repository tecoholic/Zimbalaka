[![Stories in Ready](https://badge.waffle.io/tecoholic/Zimbalaka.png?label=ready&title=Ready)](https://waffle.io/tecoholic/Zimbalaka)
# Zimbalaka
A Flask app to generate OpenZim files from select Wikipedia pages

### Pre-requisites

1. Install [OpenZim](http://www.openzim.org/wiki/OpenZIM) - For Ubuntu 14.04 `sudo apt-get install libzim-dev` [Package](http://packages.ubuntu.com/trusty/libzim-dev)
2. Get [zimwriterfs](http://sourceforge.net/p/kiwix/other/ci/master/tree/zimwriterfs/) - build and install it
3. Install [lxml](http://lxml.de/installation.html) requirements - For Ubuntu 14.04 `sudo apt-get install libxml2-dev libxslt-dev python-dev zlib1g-dev`
4. Install [Redis](http://redis.io/download) - build, install & run.

### Deploying on Ubuntu with apache2 and mod_wsgi

1. `sudo apt-get install libzim-dev libxml2-dev libxslt-dev python-dev zlib1g-dev python-pip python-virtualenv libapache2-mod-wsgi`
2. `git clone https://github.com/tecoholic/Zimbalaka.git`
3. `cd Zimbalaka`
4. `virtualenv env`
5. `. env/bin/activate`
6. `pip install -r requirements.txt`
7. Download, build. install and run redis.

        wget http://download.redis.io/releases/redis-3.0.1.tar.gz
        tar xzf redis-3.0.1.tar.gz
        cd redis-3.0.1
        make && make install
        ./utils/install_server.sh # maintain defaults except datastore location
        cd ..

7. Put `zimwriterfs` somewhere or compile and install
8. Edit `zimbalaka/default_settings.py` to reflect your production environment
8. Edit path in `celery.conf`
9. Run supervisord `supervisord -c supervisord.conf`
10. `mkdir /var/www/zimbalaka`
10. Edit path in zimbalaka.wsgi and `cp zimbalaka.wsgi /var/www/zimbalaka/zimbalaka.wsgi`
11. Configure apache2: `sudo a2enmod wsgi` and add the following to `/etc/apache2/sites-available/000-default.conf`

        WSGIDaemonProcess zimbalaka threads=5 display-name=%{GROUP}
        WSGIProcessGroup zimbalaka

        WSGIScriptAlias /zimbalaka /var/www/zimbalaka/zimbalaka.wsgi

        <Directory /var/www/zimbalaka>
            Order allow,deny
            Allow from all
        </Directory>

12. `sudo service apache2 restart`

Now the site should be live at `domain/zimbalaka`

### Developers

There are a lot of dependencies in this project which can be changed depending on the deployment situation.
* Server - Perhaps nginx + gunicorn  in place of apache2+mod_wsgi
* Celery broker - RabbitMQ in place of Redis, or even Amazon Simple Queue Service
* [Demonizing Celery](http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html) - something in place of supervisor

