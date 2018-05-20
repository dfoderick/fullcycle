'''save full cycle data'''
from helpers.queuehelper import QueueName
from domain.mining import Pool
from domain.rep import PoolRepository
from messaging.schema import PoolSchema
from fcmapp import Component

COMPONENTSAVE = Component('fullcycle')

def when_save(channel, method, properties, body):
    '''event handler when log event is raised'''
    try:
        print("[{0}] Received save message".format(COMPONENTSAVE.app.now()))
        msg = COMPONENTSAVE.app.messagedecode_configuration(body)
        dosave(msg)
    except Exception as ex:
        COMPONENTSAVE.app.logexception(ex)

def dosave(msg):
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
        sch = PoolSchema()
        pools = PoolRepository()
        pools.add(pool, COMPONENTSAVE.app.getconfigfilename('config/pools.conf'), sch)

        #update the known pools
        for known in COMPONENTSAVE.app.knownpools():
            if pool.is_same_as(known):
                oldkey = known.key
                known.named_pool = pool
                #this changes the pool key!
                known.user = pool.user
                #update the known pool (with new key)
                COMPONENTSAVE.app.update_pool(oldkey, known)

def main():
        COMPONENTSAVE.listeningqueue = COMPONENTSAVE.app.subscribe_and_listen(QueueName.Q_SAVE, when_save)

if __name__ == "__main__":
    main()

