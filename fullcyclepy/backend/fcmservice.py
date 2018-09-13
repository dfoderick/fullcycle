import os
from helpers.telegramhelper import sendalert, sendphoto
from domain.mining import Miner, Pool
from messaging.schema import MinerSchema, PoolSchema

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
