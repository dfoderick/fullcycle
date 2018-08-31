
# install sql server
sudo apt-get install mariadb-server
#setup for production
sudo mysql_secure_installation
#start service
sudo service mysql start

# on debian stretch
sudo apt-get install default-libmysqlclient-dev
sudo pip3 install mysqlclient

#run sql script to create database
sudo mysql -u root -p < ~/fullcycle/os/linux/fullcycle.sql

