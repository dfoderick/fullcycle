'''save full cycle data'''
from helpers.queuehelper import QueueName, QueueEntries
from domain.mining import Pool, Miner
from fcmapp import Component

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
        #add or update miner
        minerid = name = ipaddress = port = None
        for pair in msg.values:
            if 'minerid' in pair:
                minerid = pair['minerid']
            if 'name' in pair:
                name = pair['name']
            if 'ipaddress' in pair:
                ipaddress = pair['ipaddress']
            if 'port' in pair:
                port = pair['port']
        miner = Miner(name,'','',ipaddress,port,'','')
        COMPONENTSAVE.app.save_miner(miner)
        entries.add(QueueName.Q_MONITORMINER, COMPONENTSAVE.app.messageencode(miner))
        entries.add(QueueName.Q_PROVISION, COMPONENTSAVE.app.messageencode(miner))

    if msg.entity == 'pool':
        #save the new named pool
        pool_type = name = url = user = priority = None
        for pair in msg.values:
            if 'pool_type' in pair:
                pool_type = pair['pool_type']
            if 'name' in pair:
                name = pair['name']
            if 'url' in pair:
                url = pair['url']
            if 'user' in pair:
                user = pair['user']
            if 'priority' in pair:
                priority = pair['priority']
        pool = Pool(pool_type, name, url, user, priority)
        COMPONENTSAVE.app.save_pool(pool)
    return entries

def main():
    COMPONENTSAVE.listeningqueue = COMPONENTSAVE.app.subscribe(QueueName.Q_SAVE, when_save)
    COMPONENTSAVE.app.listen(COMPONENTSAVE.listeningqueue)

if __name__ == "__main__":
    main()
