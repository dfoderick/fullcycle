'''#discovered something that responds to cgminer api'''
from helpers.queuehelper import QueueName, QueueEntries
from backend.fcmapp import Component

COMPONENTDISCOVERED = Component(componentname='discover', option='')

def when_discovered(channel, method, properties, body):
    '''when new miner is discovered on the network'''
    try:
        print("[{0}] Received discovered notice".format(COMPONENTDISCOVERED.app.now()))
        entries = dodiscovered(COMPONENTDISCOVERED.app.messagedecodeminer(body))
        COMPONENTDISCOVERED.app.enqueue(entries)
        COMPONENTDISCOVERED.app.bus.acknowledge(COMPONENTDISCOVERED.listeningqueue, method.delivery_tag)

    except Exception as ex:
        COMPONENTDISCOVERED.app.logexception(ex)
        COMPONENTDISCOVERED.app.bus.reject(COMPONENTDISCOVERED.listeningqueue, method.delivery_tag)

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

    entries.addbroadcast(QueueName.Q_ALERT, 'discovered miner {0}'.format(miner.name))
    print("Discovered {0}".format(miner.name))
    return entries

def main():
    if COMPONENTDISCOVERED.app.isrunnow:
        miner = COMPONENTDISCOVERED.app.getknownminerbyname('S9102')
        dodiscovered(miner)
        COMPONENTDISCOVERED.app.shutdown()
    else:

        COMPONENTDISCOVERED.listeningqueue = COMPONENTDISCOVERED.app.subscribe(QueueName.Q_DISCOVERED, when_discovered, no_acknowledge=False)
        COMPONENTDISCOVERED.app.listen(COMPONENTDISCOVERED.listeningqueue)

if __name__ == "__main__":
    main()
