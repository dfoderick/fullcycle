### Install Rabbitmq natively on the OS (not recommended)
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
