#!/usr/bin/env bash
sudo apt-get dist-upgrade
sudo apt-get update
############################
# Install Useful Utilities #
############################
echo "Y" | sudo apt-get install vim
echo "Y" | sudo apt-get install curl
echo "Y" | sudo apt-get install git

###################################
# Install Apache-Related Packages #
###################################
echo "Y" | sudo apt-get install apache2
echo "Y" | sudo apt-get install libapache2-mod-fcgid
echo "Y" | sudo apt-get install libapache2-mod-xsendfile
echo "Y" | sudo apt-get install libapache2-mod-wsgi
echo "Y" | sudo apt-get install sendmail
echo "Y" | sudo apt-get install libmail-sendmail-perl

#######################################
# Install GDAL, MapServer, Etc. First #
#######################################
echo "Y" | sudo apt-get install python-software-properties
echo "Y" | sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt-get update
echo "Y" | sudo apt-get install mapserver-bin
echo "Y" | sudo apt-get install gdal-bin
echo "Y" | sudo apt-get install cgi-mapserver
echo "Y" | sudo apt-get install python-gdal
echo "Y" | sudo apt-get install python-mapscript
	
###############################################
# Add the google projection to the proj4 file #
###############################################
PROJ_FILE=/usr/share/proj/epsg
sudo printf '\n#Google Projection\n<900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs\n' | sudo tee -a $PROJ_FILE

###########################################
# Then Install PostgreSQL9.1, PostGIS 9.1 #
###########################################
echo "Y" | sudo apt-get install postgresql-9.3
echo "Y" | sudo apt-get install postgresql-client-9.3
echo "Y" | sudo apt-get install postgresql-server-dev-9.3
echo "Y" | sudo apt-get install postgresql-plperl-9.3
echo "Y" | sudo apt-get install postgresql-9.3-postgis-2.1
echo "Y" | sudo apt-get install postgresql-9.3-postgis-scripts

echo "Y" | sudo apt-get install libpq-dev

##################################
# Configure PostgreSQL / PostGIS #
##################################
# Doing some automatic config file manipulations for postgres / postgis:
DB_OWNER="postgres"
DB_NAME="lg_test_database"
DB_PASSWORD="password"
PG_VERSION=9.3
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PEER="local   all             postgres                                peer"
TRUST="local   all             postgres                                trust"
MD5="local   all             postgres                                md5"
sudo sed -i "s/$PEER/$TRUST/g" $PG_HBA
sudo sed -i "s/$MD5/$TRUST/g" $PG_HBA
sudo service postgresql restart
CREATE_SQL="create database $DB_NAME;"
psql -c "$CREATE_SQL" -U postgres
psql -c "CREATE EXTENSION postgis;" -U postgres -d $DB_NAME
psql -c "CREATE EXTENSION postgis_topology;" -U postgres -d $DB_NAME
psql -c "alter user postgres with encrypted password '$DB_PASSWORD';" -U postgres
sudo sed -i "s/$TRUST/$MD5/g" $PG_HBA
sudo service postgresql restart

########################################################################
# Install Graphics, Miscellaneous Stuff...
########################################################################
echo "Y" | sudo apt-get install python-gdal
echo "Y" | sudo apt-get install libcv-dev libopencv-dev python-opencv
echo "Y" | sudo apt-get install python-psycopg2
echo "Y" | sudo apt-get install python-setuptools
sudo easy_install -U pip
echo "Y" | sudo apt-get install python-dev
echo "Y" | sudo apt-get install python-mapscript
echo "Y" | sudo apt-get install python-scipy
sudo add-apt-repository -y ppa:mc3man/trusty-media #trusty ubuntu doesn't have an ffmpeg package (only libav)
sudo apt-get update
echo "Y" | sudo apt-get install ffmpeg
#echo "Y" | sudo apt-get install libavcodec-extra-53

############################
# Install PIP Dependencies #
############################
# there may be some problems with the map script / map server install
sudo ln -s /vagrant /localground
sudo pip install -r /vagrant/deploy_tools/requirements.txt
sudo pip install PIL==1.1.7

#############################
# Install Node.js and Bower #
#############################
curl -sL https://deb.nodesource.com/setup | sudo bash -
echo "Y" | sudo apt-get install nodejs
echo "Y" | sudo apt-get install npm
echo "Y" | sudo npm install -g bower

####################################
# Configure Local Ground on Apache #
####################################
sudo a2enmod proxy_http
sudo cp /localground/deploy_tools/apache_localground_config /etc/apache2/sites-available/localground.conf
sudo ln -s /etc/apache2/sites-available/localground /etc/apache2/sites-enabled/localground.conf
sudo cp /localground/deploy_tools/settings_local.py /localground/apps/.
sudo rm /etc/apache2/sites-enabled/000-default 
sudo service apache2 restart

###############################
# Create required directories #
###############################
cd /localground
mkdir userdata
mkdir userdata/media
mkdir userdata/prints
mkdir userdata/deleted
#Avoiding the issue w/serving django contrib static files vs. Apache's alias
sudo cp -r /usr/local/lib/python2.7/dist-packages/swampdragon/static/swampdragon /localground/static/swampdragon

###############################################
# Create required Django tables and run tests #
###############################################
cd /localground/apps
sudo ln -s /usr/lib/libgdal.so.1.17.1 /usr/lib/libgdal.so.1.17.0
#python manage.py syncdb --noinput
#python manage.py test --verbosity=2

echo '------------------------------------'
echo ' Server configured. Check it out at '
echo ' http://localhost:7777              '
echo '------------------------------------'

