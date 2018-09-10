import redis

class Cache:
    ''' in memory cache'''
    __redis = None
    isonline = False
    def __init__(self, servicelogin):
        self.encoding = 'utf-8'
        self.__redis = redis.Redis(host=servicelogin.host, port=servicelogin.port, password=servicelogin.password)
        self.isonline = True
    def iskeyexists(self, key):
        '''true when key exists in cache'''
        return self.__redis.exists(key)
    def get(self, key):
        '''get value from key'''
        try:
            return self.__redis.get(key)
        except redis.exceptions.ConnectionError as ex:
            self.isonline = False
            raise ex
    def getlist(self, key):
        '''get a list from key'''
        return self.__redis.lrange(key, 0, -1)

    def put(self, key, value):
        '''store a value into key'''
        self.__redis.set(key, value)

    def putinhashset(self, name, key, value):
        '''store value into key at name'''
        if not isinstance(value, str):
            raise ValueError('hashset value must be a string')
        self.__redis.hset(name, key, value)

    def getfromhashset(self, name, key):
        '''get value in hashset'''
        return self.__redis.hget(name, key)

    def gethashset(self, name):
        '''this will return keys and values from hashset'''
        output = {}
        hashitems = self.__redis.hgetall(name)
        for key, value in hashitems.items():
            output[key.decode(self.encoding)] = value.decode(self.encoding)
        return output
    def set(self, key, value):
        '''save value to cache key'''
        self.__redis.set(key, value)

    def delete(self, key):
        '''remove key'''
        self.__redis.delete(key)

    def hdel(self, name, key):
        '''remove key'''
        self.__redis.hdel(name, key)

    def purge(self):
        allkeys = self.__redis.scan_iter()
        for key in allkeys:
            self.delete(key)
            print("deleted key: {}".format(key))

    def close(self):
        '''close the cache'''
        self.__redis = None

class CacheKeys:
    '''all keys stored in cache'''
    knownminers = 'knownminers'
    knownpools = 'knownpools'
    knownsensors = 'knownsensors'
    #named pools, a big string. obsolete
    pools = 'pools'
    miners = 'miners'
    camera = 'camera'
