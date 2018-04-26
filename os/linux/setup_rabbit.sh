
#sonic-pi comes with erlang already installed but buggy version
sudo apt-get purge sonic-pi
sudo apt --fix-broken install
sudo apt autoremove
sudo apt-get install libjpeg8 libsctp1 libwxbase2.8-0 libwxgtk2.8-0
#download erlang
wget https://packages.erlang-solutions.com/erlang/esl-erlang/FLAVOUR_1_general/esl-erlang_20.1.7-1~raspbian~stretch_armhf.deb
#install erlang
sudo dpkg -i esl-erlang_20.1.7-1~raspbian~stretch_armhf.deb
#download rabbit
#wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.4/rabbitmq-server_3.7.4-1_all.deb
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/rabbitmq_v3_6_10/rabbitmq-server_3.6.10-1_all.deb
#install rabbit
#sudo dpkg -i rabbitmq-server_3.7.4-1_all.deb
sudo dpkg -i rabbitmq-server_3.6.10-1_all.deb
#sudo chmod 600 /var/lib/rabbitmq/.erlang.cookie
sudo rabbitmq-plugins enable rabbitmq_management

