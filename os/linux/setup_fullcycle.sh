
# install full cycle
#copy the supervisor file
sudo cp ~/fullcycle/os/linux/supervisord.conf /etc/supervisord.conf
#copy bin files
mkdir ~/bin
sudo cp -av ~/fullcycle/os/linux/fcm* ~/bin/
sudo chmod +x ~/bin/fcm*
sudo cp -av ~/fullcycle/os/linux/rabbit* ~/bin/
sudo chmod +x ~/bin/rabbit*
#install nmap for network discovery
sudo apt-get install nmap
pip3 install redis pika sqlalchemy marshmallow paramiko telethon
