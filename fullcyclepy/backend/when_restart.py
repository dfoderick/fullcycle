'''
#listens for restart command
'''
import datetime
import json
from threading import Thread
from queue import Queue
from colorama import Fore
from helpers import antminerhelper
from helpers.queuehelper import QueueName
from domain.mining import MinerCommand
from domain.logging import MinerLog
import backend.fcmutils as utils
from backend.fcmapp import Component

COMPONENTACTION = Component('action')

def enthread(target, args):
    '''put a method on a queue to be run in background'''
    thread_queue = Queue()
    def wrapper():
        thread_queue.put(target(*args))
    thread = Thread(target=wrapper)
    thread.start()
    return thread_queue

def when_restart(channel, method, properties, body):
    '''when restart command'''
    print("[{0}] Received restart command".format(str(COMPONENTACTION.app.now())))
    #TODO: restart should happen on a background thread, so that queue connection does not time out
    try:
        minermsg = COMPONENTACTION.app.messagedecodeminercommand(body)
        qreset = enthread(target=dorestart, args=(minermsg.miner, minermsg.command, ))
        qreset.get()
        COMPONENTACTION.app.bus.acknowledge(COMPONENTACTION.listeningqueue, method.delivery_tag)
    except json.decoder.JSONDecodeError as jex:
        COMPONENTACTION.app.bus.reject(COMPONENTACTION.listeningqueue, method.delivery_tag)
        COMPONENTACTION.app.logexception(jex)
        #could be json error so log the message
        COMPONENTACTION.app.logdebug(COMPONENTACTION.app.exceptionmessage(jex))
        COMPONENTACTION.app.logdebug(utils.safestring(body))
    except BaseException as ex:
        COMPONENTACTION.app.bus.reject(COMPONENTACTION.listeningqueue, method.delivery_tag)
        COMPONENTACTION.app.logexception(ex)
        print(Fore.RED+'Could not run restart command: ' + COMPONENTACTION.app.exceptionmessage(ex))

def dorestart(miner, command: MinerCommand):
    if command.command:
        showmsg = Fore.YELLOW + "{0}({1}) {2} {3}".format(miner.name, '{}:{}'.format(miner.ipaddress, miner.port), command.command, command.parameter)
        COMPONENTACTION.app.sendlog(showmsg)
        #access = COMPONENTACTION.app.antminer.getaccesslevel(miner)
        #if access == MinerAccessLevel.Restricted:
            #setting miner to privileged is taking too much cpu and hanging the controller
            #miner.set_ftp_port(COMPONENTACTION.app.configuration('discover.sshport'))
            #access = COMPONENTACTION.app.antminer.setminertoprivileged(miner)
            #if access == MinerAccessLevel.Restricted:
            #    raise Exception('Could not set miner {0} to priviledged'.format(miner.name))
        if command.parameter and command.parameter == 'reboot':
            miner.set_ftp_port(COMPONENTACTION.app.configuration.get('discover.sshport'))
            antminerhelper.reboot(miner, COMPONENTACTION.app.sshlogin())
        else:
            antminerhelper.restart(miner)
        log = MinerLog()
        log.createdate = datetime.datetime.utcnow()
        log.minerid = miner.key()
        log.minername = miner.name
        log.action = showmsg
        COMPONENTACTION.app.log_mineractivity(log)
        #antminerhelper.waitforonline(miner)
        #do something to show what current status of miner is
        #access = COMPONENTACTION.app.antminer.setminertoprivileged(miner)
        #print(access)
        #monitor so that status of miner will show offline immediately
        COMPONENTACTION.app.send(QueueName.Q_MONITORMINER, COMPONENTACTION.app.messageencode(miner))

def main():
    COMPONENTACTION.listeningqueue = COMPONENTACTION.app.subscribe(QueueName.Q_RESTART, when_restart, no_acknowledge=False)
    COMPONENTACTION.app.listen(COMPONENTACTION.listeningqueue)

if __name__ == "__main__":
    main()
