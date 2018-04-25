
create database IF NOT EXISTS fullcycle;
show databases;
use fullcycle;
show tables;
create table IF NOT EXISTS minerlog(minerlogid int NOT NULL AUTO_INCREMENT, min$
CREATE USER IF NOT EXISTS 'fullcycle'@'%' IDENTIFIED BY 'mining';
GRANT ALL PRIVILEGES ON fullcycle.* TO 'fullcycle'@'%';
exit
