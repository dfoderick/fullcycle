#Docker


!this is rabbitmq without management, use the one with management instead
docker run -d --hostname fcm-rabbit --name some-rabbit -p 5672:5672 -e RABBITMQ_DEFAULT_USER=fullcycle -e RABBITMQ_DEFAULT_PASS=mining -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' arm32v7/rabbitmq:3
!cannot use --network=host trick container does not start
! have to use -p to open port to docker processes
! only then can you get to rabbit by connection to local host (ip address of raspberry pi)
! {"name":"rabbit", "connection":"","host":"localhost","port":5672,"user":"fullcycle","password":"mining"},
!

!this is a separate instance of rabbit with web management
docker run -d --hostname fcm-rabbit --name fullcycle-rabbit -p 5672:5672 -p 8080:15672 -e RABBITMQ_DEFAULT_USER=fullcycle -e RABBITMQ_DEFAULT_PASS=mining -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' arm32v7/rabbitmq:3-management
Browse to http://raspberrypi.local:8080/

to run interactive client
docker run -it --rm --link some-rabbit:my-rabbit -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' arm32v7/rabbitmq:3 bash
easier with
docker run -it --rm --link some-rabbit:my-rabbit -e RABBITMQ_ERLANG_COOKIE='fullcyclemining' -e RABBITMQ_NODENAME=rabbit@my-rabbit arm32v7/rabbitmq:3 bash

To show what is going on with rabbit
docker logs some-rabbit

! stopping and starting fullcycle-rabbit is fine and users will persist
! if container has to be removed and run again then users have to be added again!

!copy setup into container
docker cp ~/fullcycle/os/linux/setup_rabbit_users.sh fullcycle-rabbit:setup_rabbit_users.sh
get a shell inside container
docker exec -it fullcycle-rabbit /bin/bash
bash ./setup_rabbit_users.sh
exit
