create database IF NOT EXISTS fullcycle;
show databases;
use fullcycle;
show tables;
create table IF NOT EXISTS minerlog(minerlogid int NOT NULL AUTO_INCREMENT, minerid varchar(50), minername varchar(50), createdate datetime, action varchar(255), PRIMARY KEY (minerlogid));
CREATE USER IF NOT EXISTS 'fullcycle'@'%' IDENTIFIED BY 'mining';
GRANT ALL PRIVILEGES ON fullcycle.* TO 'fullcycle'@'%';
exit
