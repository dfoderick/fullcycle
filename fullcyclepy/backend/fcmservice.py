import os
from helpers.telegramhelper import sendalert, sendphoto
from messaging.schema import MinerSchema, PoolSchema, AvailablePoolSchema, MinerCurrentPoolSchema
from domain.mining import Miner, Pool, MinerCurrentPool, AvailablePool
from domain.rep import PoolRepository
import domain.minerpool
from backend.fcmcache import CacheKeys
import backend.fcmutils as utils

class ServiceName:
    '''names of infrastructure services'''
    messagebus = 'rabbit'
    cache = 'redis'
    database = 'mysql'
    email = 'gmail'
    telegram = 'telegram'

class InfrastructureService:
    '''configuration for a dependency'''
    def __init__(self, name, connection, host, port, user, password):
        self.name = name
        self.connection = connection
        self.host = host
        self.port = port
        self.user = user
        self.password = password

class BaseService():
    def __init__(self):
        self.homedirectory = os.path.dirname(__file__)

    def getconfigfilename(self, configfilename):
        '''get the contents of a config file'''
        return os.path.join(self.homedirectory, configfilename)
    def serialize(self, entity):
        '''serialize any entity
        only need schema, message class not needed
        '''
        if isinstance(entity, Miner):
            schema = MinerSchema()
            return schema.dumps(entity).data

        if isinstance(entity, Pool):
            schema = PoolSchema()
            return schema.dumps(entity).data
        return None


class Configuration(object):
    def __init__(self, config):
        self.__config = config

    def get(self, key):
        if not key in self.__config:
            return None
        return self.__config[key]

    def is_enabled(self, key):
        lookupkey = '{0}.enabled'.format(key)
        if not lookupkey in self.__config:
            return False
        value = self.__config[lookupkey]
        if isinstance(value, str):
            return value == 'true' or value == 'True'
        return value

class PoolService(BaseService):
    def __init__(self, cache):
        super(PoolService, self).__init__()
        self.__cache = cache

    def get_all_pools(self):
        '''configured pools'''
        pools = PoolRepository().readpools(self.getconfigfilename('config/pools.conf'))
        return pools

    def findpool(self, minerpool):
        '''find a pool in list'''
        if minerpool is None:
            return None
        for pool in self.get_all_pools():
            if minerpool.currentpool == pool.url and minerpool.currentworker.startswith(pool.user):
                return pool
        return None

    def knownpools(self):
        dknownpools = self.__cache.gethashset(CacheKeys.knownpools)
        if dknownpools:
            return utils.deserializelist_withschema(AvailablePoolSchema(), list(dknownpools.values()))
        return None

    def getpool(self, miner: Miner):
        '''get pool from cache'''
        valu = self.__cache.trygetvaluefromcache(miner.name + '.pool')
        if valu is None:
            return None
        entity = MinerCurrentPool(miner, **utils.deserialize(MinerCurrentPoolSchema(), valu))
        return entity

    def add_pool(self, minerpool: domain.minerpool.MinerPool):
        '''see if pool is known or not, then add it'''
        knownpool = self.__cache.getfromhashset(CacheKeys.knownpools, minerpool.pool.key)
        if not knownpool:
            val = utils.jsonserialize(AvailablePoolSchema(), minerpool.pool)
            self.__cache.putinhashset(CacheKeys.knownpools, minerpool.pool.key, val)

    def putpool(self, pool: Pool):
        '''put pool in cache'''
        if pool and pool.name:
            valu = self.serialize(pool)
            self.__cache.tryputcache('pool.{0}'.format(pool.name), valu)

    def update_pool(self, key, pool: AvailablePool):
        self.__cache.hdel(CacheKeys.knownpools, key)
        knownpool = self.__cache.getfromhashset(CacheKeys.knownpools, pool.key)
        if not knownpool:
            val = utils.jsonserialize(AvailablePoolSchema(), pool)
            self.__cache.putinhashset(CacheKeys.knownpools, pool.key, val)

    def save_pool(self, pool: Pool):
        sch = PoolSchema()
        pools = PoolRepository()
        pools.add(pool, self.getconfigfilename('config/pools.conf'), sch)

        #update the known pools
        for known in self.knownpools():
            if pool.is_same_as(known):
                oldkey = known.key
                known.named_pool = pool
                #this changes the pool key!
                known.user = pool.user
                #update the known pool (with new key)
                self.update_pool(oldkey, known)

class Telegram(object):
    def __init__(self, config, service):
        self.configuration = config
        self.service = service

    def sendmessage(self, message):
        if self.configuration.is_enabled('telegram'):
            sendalert(message, self.service)

    def sendphoto(self, file_name):
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            if self.configuration.is_enabled('telegram'):
                sendphoto(file_name, self.service)
