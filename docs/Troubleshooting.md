# Full Cycle Mining Troubleshooting tips
Use the following guides to troubleshoot issues with Full Cycle.

## General Outline for debugging
1. Run `fcmdiag` for diagnostics. Output should appear similar to below. If there are errors then restart the affected service.
```
pi@raspberrypi:~/ $ fcmdiag
Starting application...
Starting FCM
started fullcycle
cache is working
message bus is working
database is working, 8513 logs
```
2. Once all services are running then check Full Cycle status with `fcmstatus`. All processes should have RUNNING status. If not, then stop and start processes with `fcmstop` and `fcmstart` commands.
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
3. Once Full Cycle is operating normally then the website will need to be reset with Docker.
```
pi@raspberrypi:~/ $ docker stop fullcycleweb
fullcycleweb
pi@raspberrypi:~/ $ docker start fullcycleweb
fullcycleweb
```

4. Refresh your browser and everything should be working.
5. If you continue to have problems then use `fcmlog` to see what errors are getting logged. If you believe it is an issue with Full Cycle then add the issue to GitHub.

# Full Cycle command details
Full Cycle installs some helpful commands into the ~/bin directory. You can use them to help troubleshoot and administer your installation.

## fcmdiag
This command will run diagnotics on your install and report any issues. If it reports any problems then fix those issues to see if it resolves your problem.

## fcmtest
Gets a status of your miners

## fcmstop/fcmstart
These commands stop and start Full Cyle in case it needs to be restarted.

## fcmps
This command displays information about the processes on your machine.

## docker logs fullcycleweb
This command shows the web logs.

## fcmlog
This command diplays Full Cycle process logs

## fcmupdate
Updates Full Cycle backend to master branch on GitHub

## fcmsetup
Reinstalls Full Cycle Mining

## fcmupdateweb
Updates Full Cycle front end to latest build on Docker Hub

## rabbitstart/rabbitstart/rabbitstatus
Controls rabbitmq

## fcmsimple
Does a one-time run of Full Cycle workflows for discovering, provisioning and monitoring the miners.

## Additional Troubleshooting help
Find out which version of Python you have installed.
```
python3 -V
```
It needs to be version 3.5 or higher.

Run `fcmlog` to see if it shows any output that will give you a clue
about the error.

Go to your RabbitMQ site and see if  the queues are operating correctly.
http://raspberrypi.local:15672/

# Troublehsooting supervisor
Supervisor can be restarted completely.
```
service supervisor stop
service supervisor start
```

To debug supervisord process, start supervisor in the foreground with ```supervisord -n``` to show errors. For example:
```
dfoderick@fullcycle-stretch:/etc$ supervisord -n
Error: Invalid user name pi in section 'program:fcmlog' (file: 'supervisord.conf')
For help, use /usr/local/bin/supervisord -h
```

Sometimes multiple versions of supervisor can get installed.  
Run ```whereis supervisord```
If it reports both /usr/bin and /usr/local/bin then there are two installations.
Try to uninstall one of them.
```
cd /usr/bin
sudo apt-get remove supervisor
```

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

# Other Questions

Question: Why does FullCycle not automatically discover my miner?  
Answer: FullCycle probes for port 4028 on your device which means the miner software must be running in order to identify it as a miner. Therefore, the mining software (bmminer or cgminer) must be running on the miner before it can be discovered. Please note that if there are hardware issues with the miner then the mining software will not run. Fix the hardware issue, make sure the mining software is running and then FullCycle will discover the miner.

