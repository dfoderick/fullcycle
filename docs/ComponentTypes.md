# Full Cycle Mining: An Open Source Cryptocurrency Mining Controller
David Foderick  
3/3/2018  

# Component Types
There are several flavors of components whose behavior depends on their responsibility in the workflow.
## Message Emitters. aka Generators. aka Pure Producers  
Message emitters are components that place messages onto the message bus without listening for messages themselves. In other words, they initiate a workflow. They are pure producers of messages.  
Examples: schedule and manual commands  
Schedule is a message generator that places messages on the bus at predetermined intervals. For example, a workflow for monitoring or discovery would be scheduled to execute using a scheduling component.
Manual commands would be placed on the message bus in response to a user clicking a button on a form or web page, or calling an api method. For example, the restart or shutdown command.  
[null] → mq

## Message Sinks. Aka Pure Consumers
Message Sinks are components that only listen to events and perform some action. They do not publish more messages onto the message bus. In other words they are pure consumers of messages.  
Examples: log, alert
[msg] ⇥ [null]  

# Workflow Steps
Steps are the workhorses of the workflow. They perform some business function and then pass on control to the next step in the workflow. They are both consumers (listeners, subscribers) of messages as well as producers (publishers) of messages.  
Examples: Rules, monitor, discover, etc  
For example, the rules workflow step gets run when there are new statistics messages. The rules execute logic based on the message data and create more messages (alerts) that get placed on the bus.   
[msg] -> [msg]  
## Fanouts (or Dispatchers)
Fanouts are components that receive one message and create multiple messages on a work queue to facilitate parallel processing.  
Examples: Monitor  
For example the monitor component listens for the monitor message. It then iterates (fansout) through the known miners in the system and creates a message for each miner (monitorminer). Why not just do the monitoring inside the monitor loop? If that were to happen then monitoring would be limited to the speed of that single process on that single machine. By fanning out, the work can be performed by many different worker processes that could be executed on multiple machines. In other words, the system will scale. Why not just create multiple threads? Multithreading can help but will not scale beyond one machine. A message queue is needed to coordinate between multiple processes that run on different machines.  
[msg] -> [msg,msg,msg,...]
