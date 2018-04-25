sudo rabbitmqctl add_user fullcycle mining
sudo rabbitmqctl set_user_tags fullcycle administrator
sudo rabbitmqctl set_permissions -p / fullcycle ".*" ".*" ".*"
sudo rabbitmqctl add_user action mining
sudo rabbitmqctl set_permissions -p / action ".*" ".*" ".*"
sudo rabbitmqctl add_user alert mining
sudo rabbitmqctl set_permissions -p / alert ".*" ".*" ".*"
sudo rabbitmqctl add_user component mining
sudo rabbitmqctl set_permissions -p / component ".*" ".*" ".*"
sudo rabbitmqctl add_user discover mining
sudo rabbitmqctl set_permissions -p / discover ".*" ".*" ".*"
sudo rabbitmqctl add_user email mining
sudo rabbitmqctl set_permissions -p / email ".*" ".*" ".*"
sudo rabbitmqctl add_user log mining
sudo rabbitmqctl set_permissions -p / log ".*" ".*" ".*"
sudo rabbitmqctl add_user monitor mining
sudo rabbitmqctl set_permissions -p / monitor ".*" ".*" ".*"
sudo rabbitmqctl add_user monitorminer mining
sudo rabbitmqctl set_permissions -p / monitorminer ".*" ".*" ".*"
sudo rabbitmqctl add_user offline mining
sudo rabbitmqctl set_permissions -p / offline ".*" ".*" ".*"
sudo rabbitmqctl add_user online mining
sudo rabbitmqctl set_permissions -p / online ".*" ".*" ".*"
sudo rabbitmqctl add_user provision mining
sudo rabbitmqctl set_permissions -p / provision ".*" ".*" ".*"
sudo rabbitmqctl add_user rules mining
sudo rabbitmqctl set_permissions -p / rules ".*" ".*" ".*"
sudo rabbitmqctl add_user schedule mining
sudo rabbitmqctl set_permissions -p / schedule ".*" ".*" ".*"
sudo rabbitmqctl add_user statisticsupdated mining
sudo rabbitmqctl set_permissions -p / statisticsupdated ".*" ".*" ".*"
sudo rabbitmqctl add_user test mining
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
