'''handles messages in a loop'''
from helpers.queuehelper import QueueName
from backend.when_discovered import dodiscovered
from backend.when_alert import doalert
from backend.when_provision import doprovision
from backend.when_monitorminer import domonitorminer
from backend.when_runrules import dorules
from backend.when_offline import dooffline
from backend.when_online import doonline
from backend.when_restart import dorestart

def is_queue_match(queue_name, queue_enum):
    return queue_name == queue_enum or queue_name == QueueName.value(queue_enum)

def dispatchmessages(mainapp, entries):
    '''process the messages'''
    if entries is None:
        return
    for entry in entries.entries:

        if is_queue_match(entry.queuename, QueueName.Q_DISCOVERED):
            miner = mainapp.messagedecodeminer(entry.message)
            more = dodiscovered(miner)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_ALERT):
            doalert(entry.message)

        elif is_queue_match(entry.queuename, QueueName.Q_PROVISION):
            miner = mainapp.messagedecodeminer(entry.message)
            more = doprovision(miner)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_MONITORMINER):
            miner = mainapp.messagedecodeminer(entry.message)
            more = domonitorminer(miner)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_STATISTICSUPDATED):
            msg = mainapp.messagedecodeminerstats(entry.message)
            more = dorules(msg.miner, msg.minerstats, msg.minerpool)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_OFFLINE):
            miner = mainapp.messagedecodeminer(entry.message)
            more = dooffline(miner)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_ONLINE):
            miner = mainapp.messagedecodeminer(entry.message)
            more = doonline(miner)
            dispatchmessages(mainapp, more)

        elif is_queue_match(entry.queuename, QueueName.Q_RESTART):
            minermsg = mainapp.messagedecodeminercommand(entry.message)
            dorestart(minermsg.miner, minermsg.command)
        else:
            print('{0} is not handled'.format(entry.queuename))
