'''
listens for pool switch command
'''
import datetime
from threading import Thread
from queue import Queue
from colorama import Fore
#from pika.exceptions import ChannelClosed
from helpers import antminerhelper
from helpers.queuehelper import QueueName
from domain.mining import MinerCommand, MinerAccessLevel
from domain.logging import MinerLog
from fcmapp import Component

COMPONENTACTION = Component('action')

def enthread(target, args):
    '''put a method on a queue to be run in background'''
    thread_queue = Queue()
    def wrapper():
        thread_queue.put(target(*args))
    thread = Thread(target=wrapper)
    thread.start()
    return thread_queue

def when_switch(channel, method, properties, body):
    '''Handler for pool switching'''
    try:
        print("[{0}] Received switch command".format(COMPONENTACTION.app.now()))
        minermsg = COMPONENTACTION.app.messagedecodeminercommand(body)

        qswitch = enthread(target=doswitch, args=(minermsg.miner, minermsg.command, ))
        qswitch.get()

        COMPONENTACTION.app.bus.acknowledge(COMPONENTACTION.listeningqueue, method.delivery_tag)
    except BaseException as ex:
        COMPONENTACTION.app.bus.reject(COMPONENTACTION.listeningqueue, method.delivery_tag)
        print(Fore.RED + 'Could not run switch command: ' + COMPONENTACTION.app.exceptionmessage(ex))

def doswitch(miner, command: MinerCommand):
    '''switch miner pool'''
    if command.command:
        txtalert = "{0} {1}".format(miner.name, command.command)
        print(Fore.YELLOW + txtalert)
        #check if privileged mode, raise alert if not in privileged mode!
        access = COMPONENTACTION.app.antminer.getaccesslevel(miner)
        if access == MinerAccessLevel.Restricted:
            miner.set_ftp_port(COMPONENTACTION.app.configuration('discover.sshport'))
            access = COMPONENTACTION.app.antminer.setminertoprivileged(miner)
            if access == MinerAccessLevel.Restricted:
                raise Exception('Could not set miner {0} to priviledged'.format(miner.name))
        antminerhelper.switch(miner, command.parameter)
        COMPONENTACTION.app.alert(txtalert)
        log = MinerLog()
        log.createdate = datetime.datetime.utcnow()
        log.minerid = miner.key()
        log.minername = miner.name
        log.action = txtalert
        COMPONENTACTION.app.log_mineractivity(log)
        COMPONENTACTION.app.send(QueueName.Q_MONITORMINER, COMPONENTACTION.app.messageencode(miner))

def main():
    COMPONENTACTION.listeningqueue = COMPONENTACTION.app.subscribe(QueueName.Q_SWITCH, when_switch, no_acknowledge=False)
    COMPONENTACTION.app.listen(COMPONENTACTION.listeningqueue)

if __name__ == "__main__":
    main()
