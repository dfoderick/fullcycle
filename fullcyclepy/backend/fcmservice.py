import os

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

    def sendtelegramphoto(self, file_name):
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            if self.configuration.is_enabled('telegram'):
                sendphoto(file_name, self.service)

