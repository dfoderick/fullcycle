#!/bin/bash
cd ~/
#download
wget http://download.redis.io/releases/redis-4.0.9.tar.gz
tar xzf redis-4.0.9.tar.gz
cd redis-4.0.9
make
#install
sudo make install
#setup for production
sudo mkdir /etc/redis
sudo mkdir /var/redis
sudo cp utils/redis_init_script /etc/init.d/redis_6379
#sudo cp redis.conf /etc/redis/6379.conf
sudo cp ~/fullcycle/os/linux/redis.conf /etc/redis/6379.conf
sudo mkdir /var/redis/6379
sudo update-rc.d redis_6379 start 80 2 3 4 5 . stop 20 0 1 6 .
sudo adduser --system --group --disabled-login redis --no-create-home --shell /bin/nologin --quiet
sudo chmod +x /etc/init.d/redis_6379
sudo /etc/init.d/redis_6379 start
cd ~/
#should respond with PONG
redis-cli ping
