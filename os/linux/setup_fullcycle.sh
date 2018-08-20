
# install full cycle
#copy the supervisor file
sudo service supervisord stop
sudo cp ~/fullcycle/os/linux/supervisord.conf /etc/supervisord.conf
sudo cp ~/fullcycle/os/linux/supervisor /etc/init.d/supervisord
sudo chmod +x /etc/init.d/supervisord
sudo update-rc.d supervisord defaults
sudo service supervisord start
#copy bin files
mkdir -p ~/bin
sudo cp -av ~/fullcycle/os/linux/fcm* ~/bin/
sudo chmod +x ~/bin/fcm*
sudo cp -av ~/fullcycle/os/linux/edit* ~/bin/
sudo chmod +x ~/bin/edit*
sudo cp -av ~/fullcycle/os/linux/rabbit* ~/bin/
sudo chmod +x ~/bin/rabbit*
#install nmap for network discovery
sudo apt-get -y install nmap
#install python dependencies
sudo apt-get -y install python3-picamera
pip3 install redis pika sqlalchemy marshmallow paramiko telethon python-nmap
