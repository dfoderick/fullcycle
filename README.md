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
https://github.com/dfoderick/fullcycle/wiki/Hardware-Reference
![Bitcoin Mining Controller UI](/images/FullCycleReact.png?raw=true "Bitcoin Mining Controller Web Site")
https://github.com/dfoderick/fullcyclereact

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
You should execute the installation using a ssh terminal window.

## Downloading Full Cycle Mining

```
git clone https://github.com/dfoderick/fullcycle.git
```
Any updated documentation and troubleshooting tips will be in /docs folder.
Any platform specific scripts will be in /os/linux  

Before beginning the full install, run a few preliminary steps.  
Make sure your system is up to date.
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
Install all the Python libraries that the application will need. 
Sometimes installing these can be problematic. See the troubleshooting
section if you have any problems.
```
pip3 install -r ~/fullcycle/fullcyclepy/requirements.txt
```
Install supervisor now since it will be used in the next steps.
```
sudo easy_install supervisor
```

## Installing MySql/MariaDB

The following instructions assume you are using the default password `mining`. 
Please use some kind of password. Do not leave the password blank.
Run the following script. Read and answer all prompts.
```
bash ~/fullcycle/os/linux/setup_sql.sh
```
The database should now be set up.

## Install redis

redis is the in-memory cache. Install it using the following script. 
The script uses `mining` as the default password.
```
bash ~/fullcycle/os/linux/setup_redis.sh
```
Start redis.
```
sudo /etc/init.d/redis_6379 start
```
Test your install. If the following commands can be run without error then redis is configured.
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
The script you are about to run should download and install the correct versions
that you need. However, if you need to install it yourself then here are some 
tips to follow.  
Install latest erlang for Raspbian (20.1.7 or above) BEFORE installing rabbitmq;
otherwise it installs an old version of erlang and you have to uninstall both 
rabbitmq and erlang before you can re-install!
Also install socat before rabbitmq. It should be installed from MariaDB already.  

Find latest download for Raspberry Pi at https://packages.erlang-solutions.com/erlang/#tabs-debian
  
The following script downloads and installs rabbitmq and should be all you need for
installing it on a Raspberry Pi.
```
bash ~/fullcycle/os/linux/setup_rabbit.sh
```
If everything went as expected then you can browse to the rabbitmq management site.
http://raspberrypi.local:15672/
The user set from above is `fullcycle` and the password is `mining`.

If you have any issues with the setup then please consult this online guide.

https://www.iotshaman.com/blog/content/how-to-install-rabbitmq-on-a-raspberry-pi

## Configuring Full Cycle Mining

Run the installation for FCM
```
bash ~/fullcycle/os/linux/setup_fullcycle.sh
```
A Telgram account is highly recommended to get updates from your controller 
about mining operations, photos and temperature. It is the primary
console that allows you to see what is happening to your miners.  
If you don't already have an account go to https://telegram.org/ to get set up and get your api key.  
Change the telegram configuraton in services.config to match your settings.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/services.conf
``` 
Run the following command to test your Telegram integration.  
It will prompt for your phone number and you will respond with the configrmation number. 
If successful you will get a telegram message 
with a picture from your mining controller 
(assuming you have a camera on your Raspberry Pi).
```
python3 ~/fullcycle/fullcyclepy/backend/test/test_telegram.py
```
You probably want to add your own pools. Add them to the following file.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/pools.conf
``` 
Normally, FCM should simply discover any miners on your local subnet.
If for any reason it cannot discover them 
then you would add your miners to the following file.
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/miners.conf
```
Review the application configuration settings to enable/disable hardware options and set
monitoring intervals.
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/fullcycle.conf
``` 
There are several helpful scripts that were installed in your ~/bin directory
to make using Full Cycle Mining easier. Let's use a couple of them now.  
Start up Full Cycle Mining.
```
fcmstart
```
To see the status of the processes run `fcmstatus`. You can run this any time
to check on the health of the application components.
```
fcmstatus
```
## Now What?
Congratuations on making it this far!
If everything was successful then your Full Cycle Controller
will be hard at work discovering and monitoring your miners.

But how do you see what it is doing?  
If you set up Telegram and the correct intervals in the configuration
file then you will be getting statuses sent to your Telegram account.

Your next step is to install the web site on your controller.
Hop over this project to download and install it now.  
I promise its easier to set up the web site than the back end.
https://github.com/dfoderick/fullcyclereact

