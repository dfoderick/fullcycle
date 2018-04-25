
# install sql server
sudo apt-get install mariadb-server
#setup for production
sudo mysql_secure_installation
#start service
sudo service mysql start
#run sql script to create database
sudo mysql -u root -p < ~/fullcycle/os/linux/fullcycle.sql
