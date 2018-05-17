'''#discovered something that responds to cgminer api'''
from helpers.queuehelper import QueueName, QueueEntries
from domain.mining import Miner, MinerPool
from fcmapp import Component

COMPONENTDISCOVERED = Component(componentname='discover', option='')

def when_discovered(channel, method, properties, body):
    '''when new miner is discovered on the network'''
    try:
        print("[{0}] Received discovered notice".format(COMPONENTDISCOVERED.app.now()))
        entries = dodiscovered(COMPONENTDISCOVERED.app.messagedecodeminer(body))
        COMPONENTDISCOVERED.app.enqueue(entries)
        COMPONENTDISCOVERED.listeningqueue.acknowledge(method.delivery_tag)

    except Exception as ex:
        COMPONENTDISCOVERED.app.logexception(ex)
        COMPONENTDISCOVERED.listeningqueue.reject(method.delivery_tag)

def dodiscovered(miner):
    '''then provision it'''
    entries = QueueEntries()
    entries.add(QueueName.Q_PROVISION, COMPONENTDISCOVERED.app.messageencode(miner))
    cachedminer = COMPONENTDISCOVERED.app.getminer(miner)
    #knownminer should be None
    if cachedminer is not None:
        cachedminer.updatefrom(miner)
    COMPONENTDISCOVERED.app.putminer(cachedminer)
    knownminer = COMPONENTDISCOVERED.app.getknownminer(miner)
    if knownminer is None:
        COMPONENTDISCOVERED.app.addknownminer(miner)
    else:
        COMPONENTDISCOVERED.app.updateknownminer(miner)

    namedpools = COMPONENTDISCOVERED.app.pools()
    #process the pools found on the miner
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
        COMPONENTDISCOVERED.app.add_pool(MinerPool(miner, pool.priority,pool))

    entries.add(QueueName.Q_ALERT, 'discovered miner {0}'.format(miner.name))
    print("Discovered {0}".format(miner.name))
    return entries

def main():
    '''main'''
    if COMPONENTDISCOVERED.app.isrunnow:
        miner = COMPONENTDISCOVERED.app.getknownminerbyname('S9102')
        dodiscovered(miner)
        COMPONENTDISCOVERED.app.shutdown()
    else:
        print('Waiting for messages on {0}. To exit press CTRL+C'.format(QueueName.Q_DISCOVERED))
        COMPONENTDISCOVERED.listeningqueue = COMPONENTDISCOVERED.app.makequeue(QueueName.Q_DISCOVERED)
        COMPONENTDISCOVERED.listeningqueue.subscribe(when_discovered, no_acknowledge=False)
        COMPONENTDISCOVERED.app.listen(COMPONENTDISCOVERED.listeningqueue)

if __name__ == "__main__":
    main()
