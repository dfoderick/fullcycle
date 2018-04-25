# Full Cycle Bitcoin Mining Controller
Monitoring and active management for your Bitcoin mining operation.
1. Temperature and Hashrate of ASIC miners
2. Alerts based on customizable rules
3. Switch Pools and Reset miner commands
4. Discovery of new miners on the network
5. Automatically configure miners with your pool worker accounts
6. Temperature and Humidity monitoring of your mining room
7. Photos of your mining room sent to you on a schedule
8. Configurable, Extensible architecture built on workflow components and microservices
9. Web UI for monitoring and management (https://github.com/dfoderick/fullcyclereact)

![Bitcoin Mining Controller Hardware](/images/FullCycle_Controller.png?raw=true "Bitcoin Mining Controller Hardware")
![Bitcoin Mining Controller UI](/images/FullCycleReact.png?raw=true "Bitcoin Mining Controller Web Site")

## Contents
[Requirements](#requirements)  
[Installation Overview](#installation-overview)  
[Troubleshooting](docs/Troubleshooting.md)  

## Requirements

1. Python version 3.5 (or newer)
2. Rabbit Message Broker
3. redis
4. MySql (MariaDB)

Note: Currently supported on Rasbian Stretch.

Optional:  

5. Camera for your Raspberry Pi
6. DHT22 Temperature and Humidity Sensor
7. Telegram Account

## Installation Overview

This installation assumes you are using a Raspberry Pi 
but should also work for most flavors of Linux. FCM will
run on Windows but some of the installation steps will be different.
FCM has been thoroughly tested on Rasbian Stretch.
You should execute the installation using a ssh command line.

## Downloading Full Cycle Mining

```
git clone https://github.com/dfoderick/fullcycle.git
```
Any updated documentation and troubleshooting tips will be in /docs folder.
Any platform specific scripts will be in /os/linux

Before beginning, make sure your system is up to date.
```
sudo apt-get update
```
Full Cycle Mining requires an environment setting for Python.
```
sudo nano /etc/environment
```
Add the following line to the file and save it.

PYTHONPATH=/home/pi/fullcycle/fullcyclepy

The setting does not take effect immediately. You have to `logout` and log back in.
When the environment is set correctly you will be able to print it.
```
pi@raspberrypi:~/bin $ printenv PYTHONPATH
/home/pi/fullcycle/fullcyclepy
```
Install all the Python libraries.
```
pip3 install -r requirements.txt
```
Install supervisor.
```
sudo easy_install supervisor
```

## Installing MySql/MariaDB

The following instructions assume you are using the default password `mining`. 
Please use some kind of password. Do not leave it blank.
Read and answer all prompts.
```
bash ~/fullcycle/os/linux/setup_sql.sh
```
The database should now be set up.

## Install redis

redis is the in-memory cache. Install it using the following commands. 

```
$ wget http://download.redis.io/releases/redis-4.0.9.tar.gz
$ tar xzf redis-4.0.9.tar.gz
$ cd redis-4.0.9
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
sudo mkdir /etc/redis
sudo mkdir /var/redis
sudo cp utils/redis_init_script /etc/init.d/redis_6379
sudo cp redis.conf /etc/redis/6379.conf
sudo mkdir /var/redis/6379
```
Edit the config file.
```
sudo nano /etc/redis/6379.conf
```
Set `daemonize yes`

Set `requirepass mining`

Set the logfile to `/var/log/redis_6379.log`

Set the dir to `/var/redis/6379` (very important step!)  
The next command makes redis automatically start when system is reset.
```
sudo update-rc.d redis_6379 start 80 2 3 4 5 . stop 20 0 1 6 .
```
!!! Not needed for latest Rasbian Stretch
If you get an error `insserv: warning: script 'redis_6379' missing LSB tags and overrides` then
it means you need to do this.
```
sudo nano /etc/init.d/redis_6379
```
Add the following lines under `#!/bin/sh`
```
### BEGIN INIT INFO
# Provides:             noip
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    Startup Redis
### END INIT INFO
```
!!! Not needed for latest Rasbian Stretch
Add a user that the redis service and execute under.
```
sudo adduser --system --group --disabled-login redis --no-create-home --shell /bin/nologin --quiet
sudo chmod +x /etc/init.d/redis_6379
```
Start redis.
```
sudo /etc/init.d/redis_6379 start
```
Test your install. If the following commands are run then redis is configured.
```
$ redis-cli
redis> set foo bar
OK
redis> get foo
"bar"
redis> exit
```
redis can also play ping pong.
```
redis-cli -a mining ping
```
If you have any problem installing redis then see if there are 
updated instructions at https://redis.io/topics/quickstart especially
the section "Installing Redis more properly"

## Install RabbitMQ

!!! IMPORTANT !!!  
Install latest erlang for Raspbian (20.1.7 or above) BEFORE installing rabbitmq;
otherwise it installs an old version of erlang and you have to uninstall both!
Also install socat before rabbitmq.  

Find latest download for Raspberry Pi at https://packages.erlang-solutions.com/erlang/#tabs-debian
  
The following commands download rabbitmq.
```
wget https://packages.erlang-solutions.com/erlang/esl-erlang/FLAVOUR_1_general/esl-erlang_20.1.7-1~raspbian~stretch_armhf.deb
sudo dpkg -i esl-erlang_20.1.7-1~raspbian~stretch_armhf.deb
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.4/rabbitmq-server_3.7.4-1_all.deb
sudo dpkg -i rabbitmq-server_3.7.4-1_all.deb
sudo rabbitmq-plugins enable rabbitmq_management
```
Start the rabbitmq service.
```
sudo rabbitmq-server start
```
Set up a user for each component.
```
sudo rabbitmqctl add_user fullcycle mining
sudo rabbitmqctl set_user_tags fullcycle administrator
sudo rabbitmqctl set_permissions -p / fullcycle ".*" ".*" ".*"
sudo rabbitmqctl add_user action mining
sudo rabbitmqctl set_permissions -p / action ".*" ".*" ".*"
sudo rabbitmqctl add_user alert mining
sudo rabbitmqctl set_permissions -p / alert ".*" ".*" ".*"
sudo rabbitmqctl add_user component mining
sudo rabbitmqctl set_permissions -p / component ".*" ".*" ".*"
sudo rabbitmqctl add_user discover mining
sudo rabbitmqctl set_permissions -p / discover ".*" ".*" ".*"
sudo rabbitmqctl add_user email mining
sudo rabbitmqctl set_permissions -p / email ".*" ".*" ".*"
sudo rabbitmqctl add_user log mining
sudo rabbitmqctl set_permissions -p / log ".*" ".*" ".*"
sudo rabbitmqctl add_user monitor mining
sudo rabbitmqctl set_permissions -p / monitor ".*" ".*" ".*"
sudo rabbitmqctl add_user monitorminer mining
sudo rabbitmqctl set_permissions -p / monitorminer ".*" ".*" ".*"
sudo rabbitmqctl add_user offline mining
sudo rabbitmqctl set_permissions -p / offline ".*" ".*" ".*"
sudo rabbitmqctl add_user online mining
sudo rabbitmqctl set_permissions -p / online ".*" ".*" ".*"
sudo rabbitmqctl add_user provision mining
sudo rabbitmqctl set_permissions -p / provision ".*" ".*" ".*"
sudo rabbitmqctl add_user rules mining
sudo rabbitmqctl set_permissions -p / rules ".*" ".*" ".*"
sudo rabbitmqctl add_user schedule mining
sudo rabbitmqctl set_permissions -p / schedule ".*" ".*" ".*"
sudo rabbitmqctl add_user statisticsupdated mining
sudo rabbitmqctl set_permissions -p / statisticsupdated ".*" ".*" ".*"
sudo rabbitmqctl add_user test mining
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
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
sudo cp -av ~/fullcycle/os/linux/. ~/bin/
```
Then make each one executable.
```
sudo chmod +x ~/bin/fcm*
```
A Telgram account is highly recommended to get updates from your controller 
about mining operations, photos and temperature. It is the primary
console that allows you to see what is happening to your miners.  
If you don't already have an account go to https://telegram.org/ to get set up and get your api key.  
Make any required changes to services.config.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/services.conf
``` 
Run the following command to test your Telegram integration. 
It will prompt for your phone number and you will respond with the configrmation number. If successful you will get a telegram message 
with a picture from your mining controller (assuming you have a camera on your Raspberry Pi).
```
python3 ~/fullcycle/fullcyclepy/backend/test/test_telegram.py
```
You probably want to add your own pools. Add them to this file. 
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/pools.conf
``` 
Review the application configuration settings to enable/disable hardware options and set
monitoring intervals.
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/fullcycle.conf
``` 
For discovering new miners on the network you need nmap.
```
sudo apt-get install nmap
```
Finally, start up Full Cycle Mining.
```
fcmstart
```
To see the status of the processes run `fcmstatus`.
```
fcmstatus
```
