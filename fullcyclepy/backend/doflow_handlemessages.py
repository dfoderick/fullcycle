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

#def is_queue_match(queue_name, queue_enum):
#    return queue_name == queue_enum or queue_name == QueueName.value(queue_enum)

def dispatchmessages(mainapp, entries):
    '''process the messages'''
    if entries is None:
        return

    dispatch_table = {
        QueueName.value(QueueName.Q_DISCOVERED): run_discovered,
        QueueName.value(QueueName.Q_ALERT): run_alert,
        QueueName.value(QueueName.Q_PROVISION): run_provision,
        QueueName.value(QueueName.Q_MONITORMINER): run_monitorminer,
        QueueName.value(QueueName.Q_STATISTICSUPDATED): run_statsupdated,
        QueueName.value(QueueName.Q_OFFLINE): run_offline,
        QueueName.value(QueueName.Q_ONLINE): run_online,
        QueueName.value(QueueName.Q_RESTART): run_restart,
        }

    for entry in entries.entries:
        run_method = dispatch_table[QueueName.value(entry.queuename)]
        if run_method:
            run_method(mainapp, entry)
        else:
            print('{0} is not handled'.format(entry.queuename))

def run_alert(mainapp, entry):
    doalert(entry.message)

def run_discovered(mainapp, entry):
    miner = mainapp.messagedecodeminer(entry.message)
    more = dodiscovered(miner)
    dispatchmessages(mainapp, more)

def run_provision(mainapp, entry):
    miner = mainapp.messagedecodeminer(entry.message)
    more = doprovision(miner)
    dispatchmessages(mainapp, more)

def run_monitorminer(mainapp, entry):
    miner = mainapp.messagedecodeminer(entry.message)
    more = domonitorminer(miner)
    dispatchmessages(mainapp, more)

def run_statsupdated(mainapp, entry):
    msg = mainapp.messagedecodeminerstats(entry.message)
    more = dorules(msg.miner, msg.minerstats, msg.minerpool)
    dispatchmessages(mainapp, more)

def run_offline(mainapp, entry):
    miner = mainapp.messagedecodeminer(entry.message)
    more = dooffline(miner)
    dispatchmessages(mainapp, more)

def run_online(mainapp, entry):
    miner = mainapp.messagedecodeminer(entry.message)
    more = doonline(miner)
    dispatchmessages(mainapp, more)

def run_restart(mainapp, entry):
    minermsg = mainapp.messagedecodeminercommand(entry.message)
    dorestart(minermsg.miner, minermsg.command)
