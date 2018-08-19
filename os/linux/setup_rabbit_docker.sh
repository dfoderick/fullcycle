docker run -d --hostname fcm-rabbit --name fullcycle-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=fullcycle -e RABBITMQ_DEFAULT_PASS=mining -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' --restart unless-stopped arm32v7/rabbitmq:3-management
docker cp ~/fullcycle/os/linux/setup_rabbit_users.sh fullcycle-rabbit:setup_rabbit_users.sh
docker exec -it fullcycle-rabbit /bin/bash
