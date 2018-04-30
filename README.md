# Full Cycle Bitcoin Mining Controller
Monitoring and active management for your Bitcoin mining operation.
1. Temperature and Hash rate of ASIC miners
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
Requirements to run it include the following.  

1. Python version 3.5 (or newer)
2. Rabbit Message Broker
3. redis
4. MySql (MariaDB)

The following are Optional but recommended.  

5. Camera for your Raspberry Pi
6. DHT22 Temperature and Humidity Sensor
7. Telegram Account

## Installation Overview

This installation assumes you are using a newly flashed Raspberry Pi
but should also work for most flavors of Linux. FCM can
run on Windows but some of the installation steps will be different.
FCM has been thoroughly tested on Rasbian Stretch.

The current version of Raspbian Stretch is April 2018.  
https://www.raspberrypi.org/downloads/raspbian/
Instructions on getting set up are here  
![Raspberry Pi Setup](/docs/RaspberryPiSetup.md "Raspberry Pi Setup")  

You should run the FCM installation steps using a terminal window.
You can copy and paste commands from this document into your terminal
window.  

Many of the dependencies (redis and rabbitmq) can be run from Docker.
It is highly recommended to use the Docker installation option to make it
easier, quicker and safer to manage the application.

# Docker install on Raspberry Pi
If you do not have Docker installed on your Raspberry Pi then follow these
instructions.
```
sudo apt-get install -y apt-transport-https
sudo curl -sSL https://get.docker.com | sudo sh
sudo systemctl enable docker
sudo usermod -aG docker pi
```
You will need to `logout` and log back in for permission to take effect. When you
log back in then check your Docker installation.

```
docker info
```
If you get information about your Docker program then you are ready to go.
## Downloading Full Cycle Mining
Clone the repository.
```
cd ~/
git clone https://github.com/dfoderick/fullcycle.git
```
Any platform specific scripts will be in /os/linux  

Before beginning the full install run a few preliminary steps.  
Make sure your system is up to date.
```
sudo apt-get update
sudo apt-get -y upgrade
```
Full Cycle Mining requires an environment setting for Python. And a bin directory will be needed.
```
mkdir ~/bin
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
Install supervisor now since it will be used in the next steps.
```
sudo easy_install supervisor
```
## Installing MySql/MariaDB
A database is used for logging and will be used for future
reporting features.
The following instructions assume you are using the default password `mining`.
Please use some kind of password. Do not leave the password blank.
Run the following script. Read and answer all prompts.
```
bash ~/fullcycle/os/linux/setup_sql.sh
```
The database should now be set up.

## Install redis

redis is the in-memory cache.

### Install redis using Docker
Install redis from DockerHub.
```
docker run --name fullcycle-redis -d --network=host --restart unless-stopped arm32v7/redis
```
It will tell you it can't find a local image so it
will download one from DockerHub.
If you have to install directly on the OS then Instructions
are found here [redis](docs/redis.md)
## Install RabbitMQ
Rabbitmq is the message bus that the Full Cycle components use to talk to each other.

### Install Rabbitmq using Docker (Recommended)
Download and install a preconfigured Docker image for Raspberry Pi.
```
docker run -d --hostname fcm-rabbit --name fullcycle-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=fullcycle -e RABBITMQ_DEFAULT_PASS=mining -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' --restart unless-stopped arm32v7/rabbitmq:3-management
```
Then add the required account for each component.
```
docker cp ~/fullcycle/os/linux/setup_rabbit_users.sh fullcycle-rabbit:setup_rabbit_users.sh
docker exec -it fullcycle-rabbit /bin/bash
```
You should now be at a `#` prompt inside the container. Run the setup script that creates
the accounts.
```
bash ./setup_rabbit_users.sh
exit
```
Rabbitmq is now set up.
If you have to install directly on the OS then Instructions
are found here [rabbitmq](docs/rabbitmq.md)

## Configuring Full Cycle Mining
Run the installation for FCM
```
bash ~/fullcycle/os/linux/setup_fullcycle.sh
```
Install all the Python libraries that the application will need.
Sometimes installing these can be problematic. See the ![Troubleshooting](docs/Troubleshooting.md)
section if you have any problems.
```
pip3 install -r ~/fullcycle/fullcyclepy/requirements.txt
```
You can complete the installation without a Telegram account, however
Telegram is highly recommended for you to get updates from your controller
about mining operations, photos and temperature. It is the primary
'push notification' that allows you to see what is happening to your miners.  
If you don't already have an account go to https://telegram.org/
to get set up. Create a bot for yourself using BotFather https://core.telegram.org/bots#6-botfather    
Change the telegram configuration in services.config to match your
settings. Put the BotFather token in password and chat_id in user.
Be very careful to make sure the file is valid json!
```
sudo nano ~/fullcycle/fullcyclepy/backend/config/services.conf
```
Run the following command to test your Telegram integration.  
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
If you get
redis.exceptions.ResponseError: Client sent AUTH, but no password is set
then edit services.conf and remove the redis password
Make sure all services are started. If needed, run `sudo /etc/init.d/redis_6379 start` to start redis or `rabbitstart`
to run rabbitmq.

If the test is successful it will display statistics on any miners you have set up in miners.conf.
If you just keep the default test miner in miners.conf then the output will look like this.
```
pi@raspberrypi:~ $ fcmtest
S9000   ?
Shutting down fcm app...
```
Now its time to run Full Cycle Mining!
```
fcmstart
```
This will start all processes and display a status of each running component.
To see the status of the Full Cycle components use the Supervisor web site.  
The URL is the ip address of your controller with 9009 as the default port number.  
![Full Cycle Supervisor](/images/fullcycle_supervisor.png?raw=true "Full Cycle Supervisor")
You can start and stop individual components and spy on their inner workings to see if there are any errors.  
![Full Cycle Supervisor Tail](/images/fullcycle_supervisor_tail.png?raw=true "Full Cycle Supervisor Tail")

## Now What?
Congratulations on making it this far!  
If everything was successful then your Full Cycle Controller
will be hard at work discovering and monitoring your miners.

But how do you see what the controller is doing?  
If you set up Telegram and the correct intervals in the configuration
file (fullcycle.conf) then you will be getting statuses sent to your Telegram account.

Your next step is to install the web site on your controller.
Hop over this project to download and install it now.  
https://github.com/dfoderick/fullcyclereact

If you have any problems or feedback then create an issue in this project.  

Dave Foderick  
dfoderick@gmail.com
