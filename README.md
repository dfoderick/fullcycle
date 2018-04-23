# Full Cycle Mining (FCM) Controller
Monitoring and active management for your Bitcoin mining operation.

## Requirements

1. Python version 3.5 (or newer)
2. Rabbit Message Broker
3. redis
4. MySql (MariaDB)

## Installation Overview

This installation assumes you are using a Raspberry Pi 
but should also work for most flavors of Linux. FCM will
run on Windows but some of the installation steps will be different.
FCM has been thoroughly tested on Rasbian Stretch.

## Downloading Full Cycle Mining

```
git clone https://github.com/dfoderick/fullcycle.git
```
Any updated documentation and troubleshooting tips will be in /docs folder.
Any platform specific scripts will be in /os/linux

## Installing MySql/MariaDB

You may already have the database installed. Verify using the following command.
```
pi@raspberrypi:~ $ mysql --version
mysql  Ver 15.1 Distrib 10.1.23-MariaDB, for debian-linux-gnueabihf (armv7l) using readline 5.2
```
If mysql is not installed then follow these steps. Remember the user and password. 
The following instructions assume user is `root` and password is `mining`. 
```
sudo apt-get install mysql-server
sudo mysql_secure_installation
```
Make sure the sql service is running.
```
sudo service mysql start
```
Get into the sql prompt.
```
sudo mysql -u root 
```
Execute the following commands. Hit return after each command. Don't forget the semi-colon (;) at the end of each line.
```
create database fullcycle;
show databases;
use fullcycle;
show tables;
create table minerlog(minerlogid int NOT NULL AUTO_INCREMENT, minerid varchar(50), minername varchar(50), createdate datetime, action varchar(255), PRIMARY KEY (minerlogid));
CREATE USER 'fullcycle'@'%' IDENTIFIED BY 'mining';
GRANT ALL PRIVILEGES ON fullcycle.* TO 'fullcycle'@'%'
exit
```

The database should now be set up.

## Install redis

redis is the in-memory cache. Install it using the following commands. 

```
$ wget http://download.redis.io/releases/redis-4.0.8.tar.gz
$ tar xzf redis-4.0.8.tar.gz
$ cd redis-4.0.8
$ make
```
Use the following command to copy the executables.
```
sudo make install
```
If for any reason it does not install correctly then run the following commands.
```
sudo cp src/redis-server /usr/local/bin/
sudo cp src/redis-cli /usr/local/bin/
```
Copy the configuration file from source and setup redis.
```
cp src/redis-server /etc/redis/redis.conf
```
Add a user that the redis service and execute under.
```
sudo adduser --system --group --disabled-login redis --no-create-home --shell /bin/nologin --quiet
```
Run the install.
```
cd utils
./install_server.sh
```
Test your install. If the following commands are running the redis is configured.
```
$ redis-cli
redis> set foo bar
OK
redis> get foo
"bar"
```

## Install RabbitMQ

!!! IMPORTANT !!!
Install latest erlang for Raspbian (20.1.7 or above) BEFORE installing rabbitmq;
otherwise it installs an old version of erlang and you have to uninstall both!
Also install socat before rabbitmq. You have been warned.

The following command download rabbitmq and set up a users for each component.
```
apt-get install –y erlang logrotate
sudo apt-get install socat
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/rabbitmq_v3_6_10/rabbitmq-server_3.6.10-1_all.deb
dpkg -i rabbitmq-server_3.6.10-1_all.deb
sudo rabbitmq-plugins enable rabbitmq_management
```
Start the rabbitmq service.
```
rabbitmq-server start
```
```
$ sudo rabbitmqctl add_user fullcycle mining
$ sudo rabbitmqctl set_user_tags fullcycle administrator
$ sudo rabbitmqctl set_permissions -p / fullcycle ".*" ".*" ".*"
$ sudo rabbitmqctl add_user action mining
$ sudo rabbitmqctl set_permissions -p / action ".*" ".*" ".*"
$ sudo rabbitmqctl add_user alert mining
$ sudo rabbitmqctl set_permissions -p / alert ".*" ".*" ".*"
$ sudo rabbitmqctl add_user component mining
$ sudo rabbitmqctl set_permissions -p / component ".*" ".*" ".*"
$ sudo rabbitmqctl add_user discover mining
$ sudo rabbitmqctl set_permissions -p / discover ".*" ".*" ".*"
$ sudo rabbitmqctl add_user email mining
$ sudo rabbitmqctl set_permissions -p / email ".*" ".*" ".*"
$ sudo rabbitmqctl add_user log mining
$ sudo rabbitmqctl set_permissions -p / log ".*" ".*" ".*"
$ sudo rabbitmqctl add_user monitor mining
$ sudo rabbitmqctl set_permissions -p / monitor ".*" ".*" ".*"
$ sudo rabbitmqctl add_user monitorminer mining
$ sudo rabbitmqctl set_permissions -p / monitorminer ".*" ".*" ".*"
$ sudo rabbitmqctl add_user offline mining
$ sudo rabbitmqctl set_permissions -p / offline ".*" ".*" ".*"
$ sudo rabbitmqctl add_user online mining
$ sudo rabbitmqctl set_permissions -p / online ".*" ".*" ".*"
$ sudo rabbitmqctl add_user provision mining
$ sudo rabbitmqctl set_permissions -p / provision ".*" ".*" ".*"
$ sudo rabbitmqctl add_user rules mining
$ sudo rabbitmqctl set_permissions -p / rules ".*" ".*" ".*"
$ sudo rabbitmqctl add_user schedule mining
$ sudo rabbitmqctl set_permissions -p / schedule ".*" ".*" ".*"
$ sudo rabbitmqctl add_user statisticsupdated mining
$ sudo rabbitmqctl set_permissions -p / statisticsupdated ".*" ".*" ".*"
$ sudo rabbitmqctl add_user test mining
$ sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
```
If everything went as expected then you can browse to the rabbitmq management site.
http://raspberrypi.local:15672/
The user set from above is `fullcycle` and the password is `mining`

If you have any issues with the setup then please consult this online quide.

https://www.iotshaman.com/blog/content/how-to-install-rabbitmq-on-a-raspberry-pi

## Configuring Full Cycle Mining

Copy the supervisord.conf file to its location. Make any required changes to it.
```
sudo cp ~/fullcycle/os/linux/supervisord.conf /etc/supervisord.conf
```
Included in this repository are some scripts to make managing the application easier.
Copy these to your /bin directory.
```
sudo cp ~/fullcycle/os/linux/. ~/bin/.
```
Then make each one executable.
```
sudo chmod +x ~/bin/fcm*
```
Currently, a Telgram account is required to get updates about mining operations, photos and temperature.
If you don't already have an account go to https://telegram.org/ to get set up and get your api key.  
Make any required changes to services.config.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/services.conf
``` 
Run the following command to test your Telegram integration. It will prompt for your phone number and you will respond with the configrmation number. If successful you will get a telegram message 
with a picture from your mining controller (assuming you have a camera on your Raspberry Pi).
```
python3 ~/fullcycle/fullcyclepy/backend/test/test_telegram.py
```
You probably want to add your own pools. Add them to this file. 
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/pools.conf
``` 
Finally, start up Full Cycle Mining.
```
fcmstart
```
To see the status of the processes run `fcmstatus`.
```
fcmstatus
```
