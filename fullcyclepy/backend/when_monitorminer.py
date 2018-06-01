'''#David Foderick, Skylake Software Inc.
#Runs behind firewall
'''
import time
import datetime
from threading import Thread
from queue import Queue
from colorama import Fore
import pika
from helpers.antminerhelper import MinerMonitorException, getminerinfo, stats, pools
from helpers.queuehelper import QueueName, QueueEntries
from domain import mining
from fcmapp import Component

APPMONITOR = Component('monitorminer')

def enthread(target, args):
    '''put a method on a queue to be run in background'''
    thread_queue = Queue()
    def wrapper():
        thread_queue.put(target(*args))
    thread = Thread(target=wrapper)
    thread.start()
    return thread_queue

def when_monitorminer(channel, method, properties, body):
    try:
        print("[{0}] Received monitorminer command".format(APPMONITOR.app.now()))
        APPMONITOR.app.queuestatus()
        minermsg = APPMONITOR.app.messagedecodeminer(body)
        #monitor in background so pika socket doesnt get messed up
        qmon = enthread(target=domonitorminer, args=(minermsg, ))
        APPMONITOR.app.enqueue(qmon.get())
    except Exception as ex:
        APPMONITOR.app.logexception(ex)

def domonitorminer(miner):
    '''get statistics from miner'''
    entries = QueueEntries()
    savedminer = APPMONITOR.app.getminer(miner)
    if savedminer is None:
        savedminer = miner
    try:
        #individual miner can be monitored even if manually disabled
        #todo:savedminer and knownminer out of sync. this will be fixed in refactoring redis
        if not savedminer.should_monitor() and not miner.should_monitor():
            print('skipped monitoring {0}'.format(miner.name))
            return entries
        mineroriginalstatus = savedminer.status
        start = time.perf_counter()
        minerinfo = getminerinfo(savedminer)
        minerstats = stats(savedminer)
        #minerlcd = antminerhelper.getminerlcd(miner)
        if minerstats is None:
            print('could not monitor {0}'.format(savedminer.name))
        else:
            minerpool = pools(savedminer)
            end = time.perf_counter()
            monitorperf = end - start
            #what to do if monitored miner type conflicts with saved miner type???
            #should probably provision?
            foundpool = APPMONITOR.app.findpool(minerpool)
            if foundpool is not None:
                minerpool.poolname = foundpool.name
            savedminer.monitored(minerstats, minerpool, minerinfo, monitorperf)
            if mineroriginalstatus == '':
                #first time monitoring since bootup
                print(Fore.GREEN + APPMONITOR.app.now(), savedminer.name, 'first time monitoring')
            elif savedminer.status == mining.MinerStatus.Online and (mineroriginalstatus == mining.MinerStatus.Disabled or mineroriginalstatus == mining.MinerStatus.Offline):
                #changing status from offline to online so raise event
                entries.add(QueueName.Q_ONLINE, APPMONITOR.app.messageencode(savedminer))
                print(Fore.GREEN + APPMONITOR.app.now(), savedminer.name, 'back online!')
            #TODO: if stats.elapsed < previous.elapsed then raise provision or online events

            APPMONITOR.app.putminerandstats(savedminer, minerstats, minerpool)
            #TODO:show name of current pool instead of worker
            poolname = '{0} {1}'.format(minerpool.currentpool, minerpool.currentworker)
            foundpool = APPMONITOR.app.findpool(minerpool)
            if foundpool is not None:
                poolname = foundpool.name
            print('{0} mining at {1}'.format(savedminer.name, poolname))

            #most users won't want to mine solo, so provision the miner
            if not APPMONITOR.app.configuration('mining.allowsolomining'):
                if minerpool.currentpool.startswith(APPMONITOR.app.configuration('mining.solopool')):
                    entries.add(QueueName.Q_PROVISION, APPMONITOR.app.messageencode(savedminer))

            print(Fore.CYAN+str(APPMONITOR.app.now()), savedminer.name, savedminer.status,
                  'h='+str(minerstats.currenthash), str(minerstats.minercount),
                  '{0}/{1}/{2}'.format(str(minerstats.tempboard1),
                                       str(minerstats.tempboard2),
                                       str(minerstats.tempboard3)),
                  savedminer.uptime(minerstats.elapsed),
                  '{0:0f}ms'.format(savedminer.monitorresponsetime() * 1000))
            msg = APPMONITOR.app.createmessagestats(savedminer, minerstats, minerpool)
            entries.addbroadcast(QueueName.Q_STATISTICSUPDATED, msg)

    except pika.exceptions.ConnectionClosed as qex:
        #could not enqueue a message
        print(Fore.RED + '{0} Queue Error: {1}'.format(savedminer.name,
                                                       APPMONITOR.app.exceptionmessage(qex)))
        APPMONITOR.app.logexception(qex)
    except MinerMonitorException as monitorex:
        print(Fore.RED + '{0} Miner Error: {1}'.format(savedminer.name,
                                                       APPMONITOR.app.exceptionmessage(monitorex)))
        savedminer.lastmonitor = datetime.datetime.utcnow()
        #TODO: this should be a rule. publish miner offline event
        #and let event handler decide how to handle it
        savedminer.offline_now()
        print(Fore.RED + APPMONITOR.app.now(), savedminer.name, savedminer.status)
        entries.add(QueueName.Q_OFFLINE, APPMONITOR.app.messageencode(savedminer))

    except BaseException as ex:
        print(Fore.RED+'{0} Unexpected Error in monitorminer: {1}'.format(savedminer.name,
                                                                          APPMONITOR.app.exceptionmessage(ex)))
        # we have to consider any exception to be a miner error. sets status to offline
        #if str(e) == "timed out": #(timeout('timed out',),)
        APPMONITOR.app.logexception(ex)
    #TODO: review usage of savedminer and knownminer. should only go with one
    APPMONITOR.app.putminer(savedminer)
    APPMONITOR.app.updateknownminer(savedminer)
    return entries

def main():
    '''main'''
    if APPMONITOR.app.isrunnow:
        test_miner = APPMONITOR.app.getknownminerbyname('192.168.1.177')
        if not test_miner:
            test_miner = APPMONITOR.app.getknownminerbyname('#S9000')
        if test_miner:
            domonitorminer(test_miner)
        APPMONITOR.app.shutdown()
    else:
        APPMONITOR.listeningqueue = APPMONITOR.app.subscribe(QueueName.Q_MONITORMINER, when_monitorminer)
        APPMONITOR.listen()

if __name__ == "__main__":
    main()
