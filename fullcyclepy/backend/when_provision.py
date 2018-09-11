'''# use to provision miners with default pools
# runs behind firewall
# Listens for Discovered event
'''
from threading import Thread
from queue import Queue
from colorama import Fore
from helpers import antminerhelper
from helpers.queuehelper import QueueName, QueueEntries
from domain import services
from domain.mining import MinerAccessLevel, MinerPool
from backend.fcmapp import Component

PROVISION = Component('provision', option='')

def enthread(target, args):
    '''put a method on a queue to be run in background'''
    thread_queue = Queue()
    def wrapper():
        thread_queue.put(target(*args))
    thread = Thread(target=wrapper)
    thread.start()
    return thread_queue

def when_provision(channel, method, properties, body):
    '''when provision event raised'''
    try:
        print("[{0}] Received provision command".format(PROVISION.app.now()))
        minermsg = PROVISION.app.messagedecodeminer(body)
        entries = None
        qprov = enthread(target=doprovision, args=(minermsg, ))
        while True:
            try:
                entries = qprov.get(False, timeout=3)
                break
            except Exception as ex:
                PROVISION.app.bus.sleep(3)
        PROVISION.app.enqueue(entries)
        PROVISION.app.bus.acknowledge(PROVISION.listeningqueue, method.delivery_tag)
    except Exception as ex:
        PROVISION.app.bus.reject(PROVISION.listeningqueue, method.delivery_tag)
        PROVISION.app.logexception(ex)

def doprovision(miner):
    '''provision/configure a miner'''
    entries = QueueEntries()
    poollist = PROVISION.app.pools()
    print("{0} pools configured".format(len(poollist)))
    print('{0} {1}'.format(miner.name, miner.ipaddress))
    mineraccess = ''
    addpools = None
    minerinfo = None
    minerpool = None
    try:
        minerstats, minerinfo, apicall, minerpool = antminerhelper.stats(miner)
        miner.setminerinfo(minerinfo)
        #find the current pool in known pools
        knownpool = PROVISION.app.findpool(minerpool)
        if knownpool is not None:
            minerpool.poolname = knownpool.name
        miner.minerpool = minerpool
        PROVISION.app.updateknownminer(miner)
        #find pools that need to be added and add them
        addpools = services.poolstoadd(miner, minerpool, poollist)
        mineraccess = PROVISION.app.antminer.getaccesslevel(miner)
    except antminerhelper.MinerMonitorException as ex:
        if ex.istimedout():
            mineraccess = MinerAccessLevel.Waiting
    if mineraccess == MinerAccessLevel.Restricted or mineraccess == MinerAccessLevel.Waiting:
        if mineraccess == MinerAccessLevel.Restricted:
            PROVISION.app.antminer.set_privileged(miner)
        PROVISION.app.antminer.waitforonline(miner)
        mineraccess = PROVISION.app.antminer.getaccesslevel(miner)

    if mineraccess == MinerAccessLevel.Restricted:
        entries.addalert('could not set {0} to privileged access'.format(miner.name))
        #try a few more times then give up
    else:
        addpoolstominer(miner, addpools)

        addminerpools(miner)

        switchtodefaultpool(miner, poollist, minerpool)

        enforcedefaultpool(miner, poollist, minerpool)

        entries.add(QueueName.Q_MONITORMINER, PROVISION.app.messageencode(miner))
    return entries

def enforcedefaultpool(miner, poollist, minerpool):
    #enforce default pool if it doesnt have one. find highest priority pool
    if not miner.defaultpool:
        def sort_by_priority(j):
            return j.priority
        filtered = [x for x in poollist if miner.miner_type.startswith(x.pool_type)]
        filtered.sort(key=sort_by_priority)
        #foundpriority = next((p for p in poollist if p.priority == 0), None)
        if filtered:
            switchtopool(miner, filtered[0], minerpool)

def switchtodefaultpool(miner, poollist, minerpool):
    #enforce default pool if miner has one set up
    if miner.defaultpool:
        founddefault = next((p for p in poollist if p.name == miner.defaultpool), None)
        if founddefault is not None:
            switchtopool(miner, founddefault, minerpool)

def addminerpools(miner):
    namedpools = PROVISION.app.pools()
    #process the pools found on the miner. This will pick up any pools added manually
    for pool in miner.pools_available:
        #check if pools is a named pool...
        foundnamed = None
        for namedpool in namedpools:
            if namedpool.is_same_as(pool):
                foundnamed = namedpool
                break
        if foundnamed:
            #pool should take on the cononical attributes of the named pool
            pool.named_pool = foundnamed
            pool.user = foundnamed.user
        PROVISION.app.add_pool(MinerPool(miner, pool.priority, pool))

def addpoolstominer(miner, addpools):
    for pool in addpools or []:
        print(Fore.YELLOW + "     Add", pool.name, "(addpool|{0},{1},{2})".format(pool.url, pool.user + miner.name, "x"))
        #this command adds the pool to miner and prints the result
        result = antminerhelper.addpool(miner, pool)
        if result.startswith("Access denied"):
            print(Fore.RED + result)
        else:
            print(result)


def switchtopool(miner, pooltoswitch, minerpool):
    '''switch pool'''
    if minerpool is not None:
        #find pool number of default pool and switch to it
        switchtopoolnumber = minerpool.findpoolnumberforpool(pooltoswitch.url, pooltoswitch.user)
        if switchtopoolnumber is not None and switchtopoolnumber > 0:
            antminerhelper.switch(miner, switchtopoolnumber)
            print(Fore.YELLOW + PROVISION.app.now(), miner.name, 'switched to {0}({1})'.format(pooltoswitch.name, pooltoswitch.url))
        else:
            print(Fore.RED + PROVISION.app.now(), miner.name, 'could not switch to {0}({1})'.format(pooltoswitch.name, pooltoswitch.url))

def main():
    if PROVISION.app.isrunnow or PROVISION.app.isdebug:
        for miner in PROVISION.app.knownminers():
            try:
                doprovision(miner)
            except Exception as ex:
                PROVISION.app.logexception(ex)
        PROVISION.app.shutdown()
    else:
        PROVISION.listeningqueue = PROVISION.app.subscribe(QueueName.Q_PROVISION, when_provision, no_acknowledge=False)
        PROVISION.app.listen(PROVISION.listeningqueue)

if __name__ == "__main__":
    main()
