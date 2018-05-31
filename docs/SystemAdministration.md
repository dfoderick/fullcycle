
# Full Cycle Mining: An Open Source Cryptocurrency Mining Controller
David Foderick  
3/3/2018  
## System Administration  
Intent: This document is for system administrators and IT personnel who would be responsible for operating FCM in a production environment.  
## Port configuration
Full Cycle Mining can be placed behind the firewall in the same subnet as the mining rigs. Alternatively, it can work in the DMZ as long as certain ports are open for it to communicate with the miners.  

Cgminer api port. Default is 4028  
Ssh default port 22.   

## For issuing Operating System command to the miner (example: shutdown and restart)
Full Cycle Mining is completely flexible and composable. If only monitoring is required then it can run with only port 4028 open to the miners. If full automation is required (provisioning and shutting down) then port 22 can be open as an additional step.  
If required, the monitoring function can run on a subnet with only port 4028 access to miners. The controlling functionality can run on a separate computer with only port 22 open to the miners. However, in this configuration, the two FCM servers need to communicate with each other using the message queue. By default that is port 5671.  
## Starting and Stopping Services
Normally the application will install and run as a service. If you need to start services manually then run the following commands:

##  Linux
For Linux, the commands in /os/linux are copied to the bin folder and are available for admins to run.

fcmstart  (starts Full Cycle Mining process)  
fcmstatus  (displays a status of the process)  
fcmstop  (stops the process)  
fcmdiag  (runs a diagnostic test)

## Windows
For Windows the following commands are available
startservices.cmd
fcmstart.cmd

To stop services, run the following commands:
stopservices.cmd

If your custom components require additional services to be running then put the commands in startservices.cmd and stopservices.cmd
