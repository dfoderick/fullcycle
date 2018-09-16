'''save full cycle data'''
from helpers.queuehelper import QueueName, QueueEntries
from domain.mining import Pool, Miner
from backend.fcmapp import Component

COMPONENTSAVE = Component('fullcycle')

def when_save(channel, method, properties, body):
    '''event handler when log event is raised'''
    try:
        print("[{0}] Received save message".format(COMPONENTSAVE.app.now()))
        msg = COMPONENTSAVE.app.messagedecode_configuration(body)
        entries = dosave(msg)
        COMPONENTSAVE.app.enqueue(entries)

    except Exception as ex:
        COMPONENTSAVE.app.logexception(ex)

def dosave(msg):
    entries = QueueEntries()
    if msg.entity == 'miner':
        miner = saveminer(msg)
        entries.add(QueueName.Q_MONITORMINER, COMPONENTSAVE.app.messageencode(miner))
        entries.add(QueueName.Q_PROVISION, COMPONENTSAVE.app.messageencode(miner))

    if msg.entity == 'pool':
        savepool(msg)
    return entries

def saveminer(msg):
    #add or update miner
    miner = Miner.create(msg.values)
    COMPONENTSAVE.app.save_miner(miner)
    return miner

def savepool(msg):
    #save the new named pool
    pool = Pool.create(msg.values)
    COMPONENTSAVE.app.pools.save_pool(pool)
    return pool

def main():
    COMPONENTSAVE.listeningqueue = COMPONENTSAVE.app.subscribe(QueueName.Q_SAVE, when_save)
    COMPONENTSAVE.app.listen(COMPONENTSAVE.listeningqueue)

if __name__ == "__main__":
    main()
