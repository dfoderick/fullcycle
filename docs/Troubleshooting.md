## Full Cycle Mining Troubleshooting tips

Find out which version of Python you have installed.
```
python3 -V
```
It needs to be version 3.5 or higher.

Run `fcmstatus` to see what is the status of the application.
It should show the status as RUNNING. If you see anything else then
the application is encountering an error.
```
pi@raspberrypi:~/bin $ fcmstatus
fullcycle:fcmalert               RUNNING   pid 8960, uptime 8:09:15
fullcycle:fcmcomponent           RUNNING   pid 8966, uptime 8:09:15
fullcycle:fcmdiscover            RUNNING   pid 8954, uptime 8:09:15
fullcycle:fcmdiscovered          RUNNING   pid 8961, uptime 8:09:15
fullcycle:fcmlog                 RUNNING   pid 8956, uptime 8:09:15
fullcycle:fcmmonitor             RUNNING   pid 8958, uptime 8:09:15
fullcycle:fcmmonitorminer        RUNNING   pid 8952, uptime 8:09:15
fullcycle:fcmoffline             RUNNING   pid 8957, uptime 8:09:15
fullcycle:fcmonline              RUNNING   pid 8964, uptime 8:09:15
fullcycle:fcmprovision           RUNNING   pid 8953, uptime 8:09:15
fullcycle:fcmprovisiondispatch   RUNNING   pid 8962, uptime 8:09:15
fullcycle:fcmrestart             RUNNING   pid 8955, uptime 8:09:15
fullcycle:fcmrules               RUNNING   pid 8963, uptime 8:09:15
fullcycle:fcmschedule            RUNNING   pid 8965, uptime 8:09:15
fullcycle:fcmswitch              RUNNING   pid 8959, uptime 8:09:15
```
Run `fcmlog` to see if it shows any output that will give you a clue
about the error.

Go to your RabbitMQ site and see if  the queues are operating correctly.
http://raspberrypi.local:15672/

# Troublehsooting redis
Use the following command when testing redis installed Natively.
These commands will not work when using the Docker install of redis.
If the following commands can be run without error then redis is configured.
```
$ redis-cli
redis> set foo bar
OK
redis> get foo
"bar"
redis> exit
```
redis can also play ping pong.
```
redis-cli -a mining ping
```
If you have any problem installing redis then see if there are
updated instructions at https://redis.io/topics/quickstart especially
the section "Installing Redis more properly"
