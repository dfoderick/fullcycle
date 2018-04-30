rabbitmqctl add_user fullcycle mining
rabbitmqctl set_user_tags fullcycle administrator
rabbitmqctl set_permissions -p / fullcycle ".*" ".*" ".*"
rabbitmqctl add_user action mining
rabbitmqctl set_permissions -p / action ".*" ".*" ".*"
rabbitmqctl add_user alert mining
rabbitmqctl set_permissions -p / alert ".*" ".*" ".*"
rabbitmqctl add_user component mining
rabbitmqctl set_permissions -p / component ".*" ".*" ".*"
rabbitmqctl add_user discover mining
rabbitmqctl set_permissions -p / discover ".*" ".*" ".*"
rabbitmqctl add_user email mining
rabbitmqctl set_permissions -p / email ".*" ".*" ".*"
rabbitmqctl add_user log mining
rabbitmqctl set_permissions -p / log ".*" ".*" ".*"
rabbitmqctl add_user monitor mining
rabbitmqctl set_permissions -p / monitor ".*" ".*" ".*"
rabbitmqctl add_user monitorminer mining
rabbitmqctl set_permissions -p / monitorminer ".*" ".*" ".*"
rabbitmqctl add_user offline mining
rabbitmqctl set_permissions -p / offline ".*" ".*" ".*"
rabbitmqctl add_user online mining
rabbitmqctl set_permissions -p / online ".*" ".*" ".*"
rabbitmqctl add_user provision mining
rabbitmqctl set_permissions -p / provision ".*" ".*" ".*"
rabbitmqctl add_user rules mining
rabbitmqctl set_permissions -p / rules ".*" ".*" ".*"
rabbitmqctl add_user schedule mining
rabbitmqctl set_permissions -p / schedule ".*" ".*" ".*"
rabbitmqctl add_user statisticsupdated mining
rabbitmqctl set_permissions -p / statisticsupdated ".*" ".*" ".*"
rabbitmqctl add_user test mining
rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
