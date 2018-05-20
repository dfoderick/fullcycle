'''handles messages in a loop'''
from helpers.queuehelper import QueueName
from when_discovered import dodiscovered
from when_alert import doalert
from when_provision import doprovision
from when_monitorminer import domonitorminer
from when_runrules import dorules
from when_offline import dooffline
from when_online import doonline
from when_restart import dorestart

def dispatchmessages(mainapp, entries):
    '''process the messages'''
    if entries is None:
        return
    for entry in entries.entries:

        if entry.queuename == QueueName.Q_DISCOVERED:
            miner = mainapp.messagedecodeminer(entry.message)
            more = dodiscovered(miner)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_ALERT:
            doalert(entry.message)

        elif entry.queuename == QueueName.Q_PROVISION:
            miner = mainapp.messagedecodeminer(entry.message)
            more = doprovision(miner)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_MONITORMINER:
            miner = mainapp.messagedecodeminer(entry.message)
            more = domonitorminer(miner)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_STATISTICSUPDATED:
            msg = mainapp.messagedecodeminerstats(entry.message)
            more = dorules(msg.miner, msg.minerstats, msg.minerpool)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_OFFLINE:
            miner = mainapp.messagedecodeminer(entry.message)
            more = dooffline(miner)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_ONLINE:
            miner = mainapp.messagedecodeminer(entry.message)
            more = doonline(miner)
            dispatchmessages(mainapp, more)

        elif entry.queuename == QueueName.Q_RESTART:
            minermsg = mainapp.messagedecodeminercommand(entry.message)
            dorestart(minermsg.miner, minermsg.command)
        else:
            print('{0} is not handled'.format(entry.queuename))
