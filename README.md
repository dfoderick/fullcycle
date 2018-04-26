# Full Cycle Bitcoin Mining Controller
Monitoring and active management for your Bitcoin mining operation.
1. Temperature and Hashrate of ASIC miners
2. Alerts based on customizable rules
3. Switch Pools and Reset miner commands
4. Discover new miners on the network
5. Automatically configure miners with your pool worker accounts
6. Temperature and Humidity monitoring of your mining room
7. Photos of your mining room sent to you on a schedule
8. Configurable, extensible architecture built on workflow components and microservices
9. Web UI for monitoring and management (https://github.com/dfoderick/fullcyclereact)

![Bitcoin Mining Controller Hardware](/images/FullCycle_Controller.png?raw=true "Bitcoin Mining Controller Hardware")
https://github.com/dfoderick/fullcycle/wiki/Hardware-Reference
![Bitcoin Mining Controller UI](/images/FullCycleReact.png?raw=true "Bitcoin Mining Controller Web Site")
https://github.com/dfoderick/fullcyclereact

## Contents
[Requirements](#requirements)  
[Installation Overview](#installation-overview)  
[Troubleshooting](docs/Troubleshooting.md)  
[Next Steps](#now-what)  

## Requirements

Full Cycle Mining has been tested on Antminer S9, A3 and D3.  

1. Python version 3.5 (or newer)
2. Rabbit Message Broker
3. redis
4. MySql (MariaDB)

Optional:  

5. Camera for your Raspberry Pi
6. DHT22 Temperature and Humidity Sensor
7. Telegram Account

## Installation Overview

This installation assumes you are using a newly flashed Raspberry Pi
but should also work for most flavors of Linux. FCM can
run on Windows but some of the installation steps will be different.
FCM has been thoroughly tested on Rasbian Stretch.

The current version of Rasbian Stretch is April 2018.  
https://www.raspberrypi.org/downloads/raspbian/
Instructions on getting set up are here  
![Raspberry Pi Setup](/docs/RaspberryPiSetup.md?raw=true "Raspberry Pi Setup")  

You should run the FCM installation steps using a terminal window.  

## Downloading Full Cycle Mining
Clone the repository.
```
git clone https://github.com/dfoderick/fullcycle.git
```
Any updated documentation and troubleshooting tips will be in /docs folder.
Any platform specific scripts will be in /os/linux  

Before beginning the full install run a few preliminary steps.  
Make sure your system is up to date.
```
sudo apt-get update
sudo apt-get upgrade
```
Full Cycle Mining requires an environment setting for Python.
```
sudo nano /etc/environment
```
Add the following line to the file and save it.

PYTHONPATH=/home/pi/fullcycle/fullcyclepy  

The setting does not take effect immediately. You have to `sudo reboot` and log back in.
When the environment is set correctly you will be able to print it.
```
pi@raspberrypi:~/bin $ printenv PYTHONPATH
/home/pi/fullcycle/fullcyclepy
```
Install supervisor now since it will be used in the next steps.
```
sudo easy_install supervisor
```

## Installing MySql/MariaDB

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
Restart the controller at this point.
```
sudo reboot
```
When you can log back in again then make sure rabbitmq is running.
```
sudo service rabbitmq-server start
```
You can check the status of the rabbitmq service.
```
sudo service rabbitmq-server status
```
If there were errors installing then you can try unintall and re-running the script.
```
sudo dpkg -r rabbitmq-server
sudo dpkg -r esl-erlang
bash ~/fullcycle/os/linux/setup_rabbit.sh
```
Once rabbitmq is running then you can add the users.
```
bash ~/fullcycle/os/linux/setup_rabbit_users.sh
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
Install all the Python libraries that the application will need.
Sometimes installing these can be problematic. See the troubleshooting
section if you have any problems.
```
pip3 install -r ~/fullcycle/fullcyclepy/requirements.txt
```
You can complete the installation without a Telegram account, however
Telgram is highly recommended for you to get updates from your controller
about mining operations, photos and temperature. It is the primary
'push notification' that allows you to see what is happening to your miners.  
If you don't already have an account go to https://telegram.org/
to get set up and get your api key.  
Change the telegram configuraton in services.config to match your
settings for name and api key.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/services.conf
```
Run the following command to test your Telegram integration.  
It will prompt for your phone number (use international format beginning with '1' if you
are in the USA)
and you will respond with the configrmation number that gets sent to you in Telegram.
If successful you will get a telegram message ('Full Cycle Mining Test ...')
with a picture from your mining controller
(assuming you have a camera on your Raspberry Pi).
```
python3 ~/fullcycle/fullcyclepy/tests/test_telegram.py
```
If you get any errors running the test - don't worry. Either you do not have a
camera installed on your Pi or else you are missing an installation step.
We'll get to them in the next section.

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
Start up Full Cycle Mining. (You may have to `logout` and log back in to make these work.)
```
fcmtest
```
If there are any errors listed then (missing imports) then fix them.
Make sure all services are started. If needed, run `sudo /etc/init.d/redis_6379 start` to start redis or `rabbitstart`
to run rabbitmq.

If the test is successfull it will get statistics on any miners you have set up in miners.conf.

Now its time to run Full Cycle Mining!
```
fcmstart
```
This will start all processes and display a status of each one.
To see the status of the Full Cycle components use the Supervisor web site.  
The url is the ipaddress of your controller with 9009 as the default port number.  
![Full Cycle Supervisor](/images/fullcycle_supervisor.png?raw=true "Full Cycle Supervisor")
You can start and stop individual components and spy on their inner workings.  
![Full Cycle Supervisor Tail](/images/fullcycle_supervisor_tail.png?raw=true "Full Cycle Supervisor Tail")

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
