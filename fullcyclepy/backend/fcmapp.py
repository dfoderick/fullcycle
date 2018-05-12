'''Application Service layer for Full Cycle Mining
Gateway into most of application functionality'''
import sys
import os
#import os.path
import datetime
import logging
import json
import base64
from colorama import init
from colorama import Fore
import redis
import pika
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from domain.mining import Miner, MinerCurrentPool, MinerStatistics, MinerStatus
from domain.rep import MinerRepository, PoolRepository, LoginRepository, RuleParametersRepository, BaseRepository
#from domain.miningrules import RuleParameters
from messaging.messages import Message, MessageSchema, MinerMessageSchema
from domain.sensors import Sensor, SensorValue
from messaging.sensormessages import SensorValueMessage, SensorValueSchema
from messaging.schema import MinerSchema, MinerStatsSchema, MinerCurrentPoolSchema
from helpers.queuehelper import QueueName, Queue, BroadcastListener, BroadcastSender, QueueEntry, QueueType
from helpers.camerahelper import take_picture
from helpers.antminerhelper import MinerMonitorException, setminertoprivileged, privileged, setprivileged, setrestricted, waitforonline, restartminer, restart
from helpers.temperaturehelper import readtemperature
from helpers.telegramhelper import sendalert, sendphoto

class ComponentName:
    '''names of components, corresponds to queue login names'''
    fullcycle = 'fullcycle'
    rules = 'rules'

class Component(object):
    '''A component is a unit of execution of FCM'''
    def __init__(self, componentname, option=''):
        self.app = ApplicationService(component=componentname, option=option)
        self.listeningqueue = None

class ServiceName:
    '''names of infrastructure services'''
    messagebus = 'rabbit'
    cache = 'redis'
    database = 'mysql'
    email = 'gmail'

class InfrastructureService:
    '''configuration for a dependency'''
    name = ''
    connection = ''
    host = ''
    port = ''
    user = ''
    password = ''
    def __init__(self, name, connection, host, port, user, password):
        self.name = name
        self.connection = connection
        self.host = host
        self.port = port
        self.user = user
        self.password = password

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
    def close(self):
        '''close the cache'''
        self.__redis = None

class CacheKeys:
    '''all keys stored in cache'''
    knownminers = 'knownminers'
    knownsensors = 'knownsensors'
    pools = 'pools'
    miners = 'miners'
    camera = 'camera'

class Antminer():
    def __init__(self, config, login):
        self.__config = config
        self.__login = login

    def set_privileged(self, miner):
        setprivileged(miner, self.__login, self.__config['provision.apiallow.privileged'])

    def setminertoprivileged(self, miner):
        return setminertoprivileged(miner, self.__login, self.__config['provision.apiallow.privileged'])

    def set_restricted(self, miner):
        setrestricted(miner, self.__login, self.__config['provision.apiallow.restricted'])

    def waitforonline(self, miner):
        return waitforonline(miner)

    def getaccesslevel(self, miner):
        return privileged(miner)

    def restart(self, miner):
        return restart(miner)

    def restartssh(self, miner):
        '''restart miner through ssh'''
        return restartminer(miner, self.__login)


class ApplicationService:
    '''Application Services'''
    programnamefull = ''
    programname = ''
    component = ComponentName.fullcycle
    #true if user passed in -now command line argument
    isrunnow = False
    #dictionary of queues managed by this app
    _queues = {}
    #the startup directory
    homedirectory = None
    __cache = None
    __config = {}
    __logger = None
    __logger_debug = None
    __logger_error = None
    antminer = None

    def __init__(self, component=ComponentName.fullcycle, option=None, announceyourself = False):
        self.component = component
        self.initargs(option)
        self.startupstuff()
        self.setup_configuration()
        self.initlogger()
        if self.component == ComponentName.fullcycle:
            self.loginfo('Starting FCM')
        self.initmessaging()
        #this is slow. should be option to opt out of cache?
        self.initcache()
        self.init_application()
        self.init_sensors()
        if announceyourself:
            self.sendqueueitem(QueueEntry(QueueName.Q_LOG, '{0} Started {1}'.format(self.now(), self.component), QueueType.broadcast))

    def initargs(self, option):
        '''process command line arguments'''
        if sys.argv:
            self.programnamefull = sys.argv[0]
            self.programname = os.path.basename(self.programnamefull)
        firstarg = option
        if len(sys.argv) > 1:
            firstarg = sys.argv[1]
        if firstarg is not None:
            if firstarg == '-now':
                self.isrunnow = True

    def startupstuff(self):
        '''start up the application'''
        self.homedirectory = os.path.dirname(__file__)
        #used with colorama on windows
        init(autoreset=True)

    def initmessaging(self):
        '''start up messaging'''
        self._schemamsg = MessageSchema()

    def initcache(self):
        '''start up cache'''
        try:
            cachelogin = self.getservice(ServiceName.cache)
            self.__cache = Cache(cachelogin)
            #this is ok until list of miners gets too big
            self.initminercache()
        except Exception as ex:
            #cache is offline. try to run in degraded mode
            self.logexception(ex)

    def init_sensors(self):
        self.sensor = Sensor('controller', 'DHT22', 'controller')

    def init_application(self):
        self.antminer = Antminer(self.__config, self.sshlogin())

    def getconfigfilename(self, configfilename):
        '''get the contents of a config file'''
        return os.path.join(self.homedirectory, configfilename)

    def setup_configuration(self):
        '''configuration is loaded once at startup'''
        raw = BaseRepository().readrawfile(self.getconfigfilename('config/fullcycle.conf'))
        self.__config = json.loads(raw)

    def configuration(self, key):
        return self.__config[key]

    def is_enabled_configuration(self, key):
        lookupkey = '{0}.enabled'.format(key)
        if not lookupkey in self.__config:
            return False
        value = self.__config[lookupkey]
        if isinstance(value,str):
            return (value == 'true' or value == 'True')
        return value

    def initminercache(self):
        '''put known miners into cache'''
        if self.__cache.get(CacheKeys.pools) is None:
            spools = PoolRepository().readrawfile(self.getconfigfilename('config/pools.conf'))
            self.tryputcache(CacheKeys.pools, spools)

        if self.__cache.get(CacheKeys.miners) is None:
            sminers = MinerRepository().readrawfile(self.getconfigfilename('config/miners.conf'))
            self.tryputcache(CacheKeys.miners, sminers)

        for miner in self.miners():
            #status is not persisted yet so init from name
            if miner.is_manually_disabled():
                miner.status = MinerStatus.Disabled
            if self.getminer(miner) is None:
                self.putminer(miner)

    def cacheclear(self):
        '''clear the cache'''
        for miner in self.miners():
            self.__cache.delete(miner.name)
        self.__cache.delete(CacheKeys.knownminers)
        self.__cache.delete(CacheKeys.knownsensors)

    def initlogger(self):
        '''set up logging application info'''
        self.__logger = self.setup_logger('fcmapp', 'fcm.log', logging.INFO)

        self.__logger_debug = self.setup_logger('fcmdebug', 'fcm.bug', logging.DEBUG)

        self.__logger_error = self.setup_logger('fcmerror', 'fcm.err', logging.ERROR)

    def setup_logger(self, logger_name, log_file, level=logging.INFO):
        '''start logger'''
        logr = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        #by default will append. use mode='w' to overwrite
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logr.addHandler(file_handler)
        # is setting stream necessary
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logr.setLevel(level)
        return logr

    def loginfo(self, message):
        '''log informational message'''
        logmsg = '{0}: {1}'.format(self.programname, message)
        self.__logger.info(logmsg)
        print(message)

    def logerror(self, message):
        '''log error'''
        logmsg = '{0}: {1}'.format(self.programname, message)
        self.__logger_error.error(logmsg)
        print(Fore.RED+logmsg)

    def logdebug(self, message):
        '''log debug message'''
        logmsg = '{0}: {1}'.format(self.programname, message)
        self.__logger_debug.debug(logmsg)
        print(Fore.GREEN+logmsg)

    def print(self, message):
        '''echo message to screen'''
        print(message)

    def now(self):
        '''current time formatted as friendly string'''
        return self.formattime(datetime.datetime.now())

    def formattime(self, time):
        '''standard format for time'''
        return time.strftime('%Y-%m-%d %H:%M:%S')

    #region lookups
    #todo: move to configurations section
    def miners(self):
        '''configured miners'''
        miners = MinerRepository().readminers(self.getconfigfilename('config/miners.conf'))
        return miners

    def knownminers(self):
        '''for now just return a list of miners
        later should consider returning a list that is easily searched and filtered
        '''
        dknownminers = self.__cache.gethashset(CacheKeys.knownminers)
        if dknownminers is not None and dknownminers:
            #get list of miners from cache
            return self.deserializelistofstrings(list(dknownminers.values()))
        knownminers = self.miners()
        return knownminers

    def knownsensors(self):
        dknownsensors = self.__cache.gethashset(CacheKeys.knownsensors)
        if dknownsensors is not None and dknownsensors:
            return self.deserializelistofstrings(list(dknownsensors.values()))
        return None

    def addknownsensor(self, sensorvalue):
        val = self.jsonserialize(SensorValueSchema(), sensorvalue)
        self.__cache.putinhashset(CacheKeys.knownsensors, sensorvalue.sensorid, val)

    def updateknownsensor(self, sensorvalue):
#        ssensor = self.__cache.getfromhashset(CacheKeys.knownsensors, sensorvalue.sensorid)
#        memsensor = self.deserialize(SensorValueSchema(), self.safestring(ssensor))
        val = self.serialize(memminer)
        self.__cache.putinhashset(CacheKeys.knownsensors, sensor.sensorid, val)

    def minersummary(self, maxNumber = 10):
        '''show a summary of known miners
        '''
        return '\n'.join([m.summary() for m in self.knownminers()[:maxNumber]])

    def addknownminer(self, miner):
        '''add miner to known miners list'''
        val = self.serialize(miner)
        self.__cache.putinhashset(CacheKeys.knownminers, miner.key(), val)

    def updateknownminer(self, miner):
        '''update known miner in cache'''
        sminer = self.__cache.getfromhashset(CacheKeys.knownminers, miner.key())
        memminer = self.deserialize(MinerSchema(), self.safestring(sminer))
        if memminer is None:
            memminer = miner
        else:
            #merge new values
            memminer.updatefrom(miner)
        val = self.serialize(memminer)
        self.__cache.putinhashset(CacheKeys.knownminers, miner.key(), val)

    def pools(self):
        '''configured pools'''
        pools = PoolRepository().readpools(self.getconfigfilename('config/pools.conf'))
        return pools

    def findpool(self, minerpool):
        '''find a pool in list'''
        if minerpool is None: return None
        for pool in self.pools():
            if minerpool.currentpool == pool.url and minerpool.currentworker.startswith(pool.user):
                return pool
        return None

    def sshlogin(self):
        '''return contents of login file'''
        return self.readlogin('ftp.conf')

    def readlogin(self, filename):
        '''read login file configuration'''
        login = LoginRepository().readlogins(self.getconfigfilename('config/'+filename))
        return login

    def ruleparameters(self):
        '''rules parameters'''
        return RuleParametersRepository().readrules(self.getconfigfilename('config/'+'rules.conf'))

    def getservice(self, servicename):
        '''get a service by name. should be repository'''
        file_name = self.getconfigfilename('config/services.conf')
        with open(file_name, encoding='utf-8-sig') as config_file:
            content = json.loads(config_file.read())
        services = [InfrastructureService(**s) for s in content]
        return next((s for s in services if s.name == servicename), None)

    def getservice_useroverride(self, servicename):
        service = self.getservice(servicename)
        service.user = self.component
        return service
    #endregion lookups

    def listen(self, qlisten: Queue):
        """Goes into listening mode on a queue"""
        self.registerqueue(qlisten)
        try:
            qlisten.listen()
        except KeyboardInterrupt:
            self.shutdown()
        except BaseException as unhandled:
            self.unhandledexception(unhandled)

    def registerqueue(self, qregister: Queue):
        '''register a queue'''
        if qregister.queue_name not in self._queues.keys():
            self._queues[qregister.queue_name] = qregister

    def shutdown(self, exitstatus=None):
        '''shut down app services'''
        self.loginfo('Shutting down fcm app...')
        self.closequeues()
        if self.__cache is not None:
            self.__cache.close()
        sys.exit(exitstatus)

    def closequeue(self, thequeue):
        '''close the queue'''
        if thequeue is None: return
        try:
            if thequeue is not None:
                thequeue.close()
            del self._queues[thequeue.queue_name]
        except Exception as ex:
            self.logexception(ex)

    def closequeues(self):
        '''close a bunch of queues'''
        for k in list(self._queues):
            self.closequeue(self._queues[k])

    def unhandledexception(self, unhandled):
        '''what to do when there is an exception that app cannot handle'''
        self.logexception(unhandled)

    def exceptionmessage(self, ex):
        '''gets exception message even when it doesnt have one'''
        exc_type, _, exc_tb = sys.exc_info()
        exmsg = getattr(ex, 'message', repr(ex))
        return '{0}:{1}:{2}'.format(exc_type, exc_tb.tb_lineno, exmsg)

    def logexception(self, ex):
        '''log an exception'''
        self.logerror(self.exceptionmessage(ex))

    def sendlog(self, logmessage):
        '''send message to log queue'''
        item = QueueEntry(QueueName.Q_LOG, logmessage, 'broadcast')
        self.sendqueueitem(item)
        print(logmessage)

    def makequeue(self, qname, userlogin=None):
        '''create a queue from the name'''
        thelogin = userlogin
        if userlogin is None:
            thelogin = self.component
        service_login = self.getservice(ServiceName.messagebus)
        service_login.user = thelogin
        thequeue = Queue(qname, service_login)
        self.registerqueue(thequeue)
        return thequeue

    def subscribe(self, q_name, callback, no_acknowledge=True):
        '''subscribe to a queue'''
        thequeue = Queue(q_name, self.getservice_useroverride(ServiceName.messagebus))
        print('Waiting for messages on {0}. To exit press CTRL+C'.format(q_name))
        thequeue.subscribe(callback, no_acknowledge=no_acknowledge)
        return thequeue

    #[obsolete], caller needs reference to q before listening
    def subscribe_and_listen(self, q_name, callback, no_acknowledge=True):
        '''listen to a queue'''
        thequeue = self.subscribe(q_name, callback, no_acknowledge=True)
        self.listen(thequeue)
        #this will never return because listen is blocking call
        return thequeue

    def makebroadcastlistener(self, broadcast_name):
        broadcast = BroadcastListener(broadcast_name, servicelogin=self.getservice_useroverride(ServiceName.messagebus))
        return broadcast

    def listen_to_broadcast(self, broadcast_name, callback, no_acknowledge=True):
        thebroadcast = self.makebroadcastlistener(broadcast_name)
        print('Waiting for messages on {0}. To exit press CTRL+C'.format(thebroadcast.queue_name))
        thebroadcast.subscribe(callback, no_acknowledge=no_acknowledge)
        self.listen(thebroadcast)
        return thebroadcast

    def trypublish(self, thequeue, msg: str):
        '''publish a message to the queue'''
        try:
            thequeue.publish(msg)
            return True
        except pika.exceptions.ConnectionClosed as ex:
            logmessage = 'Error publishing to {0} {1}'.format(thequeue.queue_name, self.exceptionmessage(ex))
            self.logerror(logmessage)
            return False

    def trybroadcast(self, thequeue, msg):
        '''broadcase a message to all queue listeners'''
        try:
            thequeue.broadcast(msg)
            return True
        except pika.exceptions.ConnectionClosed as conxex:
            self.logerror('Error broadcasting to {0} {1}'.format(thequeue.queue_name, self.exceptionmessage(conxex)))
            return False

    def queuestatus(self):
        """TODO:print queue status"""
        pass
        #for q in self._queues.values():
        #    print(q.queue_name,str(q._connection))

    def putminer(self, miner: Miner):
        '''put miner in cache'''
        if miner:
            valu = self.serialize(miner)
            self.tryputcache('miner.{0}'.format(miner.key()), valu)

    def getminer(self, miner: Miner):
        '''strategies for getting miner from cache
        originally was key=miner.name but that was not good
        changed to key='miner.'+minerid
        '''
        valu = self.trygetvaluefromcache('miner.{0}'.format(miner.key()))
        if valu is None:
            return None
        minerfromstore = self.deserialize(MinerSchema(), self.safestring(valu))
        minerfromstore.store = 'mem'
        return minerfromstore

    def getknownminer(self, miner: Miner):
        '''get a known miner'''
        return self.getknownminerbyname(miner.key())

    def getminerbyname(self, minername):
        filtered = [x for x in self.miners() if x.name == minername]
        if filtered: return filtered[0]
        return None

    def getknownminerbyname(self, minername):
        '''todo: rename to bykey'''
        str_miner = self.__cache.getfromhashset(CacheKeys.knownminers, minername)
        if str_miner is None:
            return None
        return self.deserialize(MinerSchema(), self.safestring(str_miner))

    def tryputcache(self, key, value):
        '''put value in cache key'''
        if value is None: return
        try:
            if self.__cache is not None:
                self.__cache.set(key, value)
        except redis.exceptions.ConnectionError as ex:
            self.logexception(ex)

    def putminerandstats(self, miner: Miner, minerstats, minerpool):
        '''put miner and status in cache'''
        self.putminer(miner)
        schema = MinerStatsSchema()
        valstats = schema.dumps(minerstats).data
        self.tryputcache(miner.key() + '.stats', valstats)
        schema = MinerCurrentPoolSchema()
        valpool = schema.dumps(minerpool).data
        self.tryputcache(miner.key() + '.pool', valpool)

    def trygetvaluefromcache(self, key):
        '''get value from cache'''
        if self.__cache is not None:
            try:
                return self.__cache.get(key)
            except Exception as ex:
                self.logexception(ex)
        return None

    def getstats(self, miner: Miner):
        '''get stats entity'''
        valu = self.trygetvaluefromcache(miner.name + '.stats')
        if valu is None: return None
        entity = MinerStatistics(miner, **self.deserialize(MinerStatsSchema(), valu))
        return entity

    def getpool(self, miner: Miner):
        '''get pool from cache'''
        valu = self.trygetvaluefromcache(miner.name + '.pool')
        if valu is None: return None
        entity = MinerCurrentPool(miner, **self.deserialize(MinerCurrentPoolSchema(), valu))
        #entity.Miner = miner
        return entity

    def safestring(self, thestring):
        '''safely convert anything into string'''
        if thestring is None: return None
        if isinstance(thestring, str): return thestring
        return str(thestring, "utf-8")

    def getminerstatscached(self):
        '''iterator for cached stats'''
        for miner in self.miners():
            yield (self.getminer(miner), self.getstats(miner), self.getpool(miner))

    def messagedecodeminer(self, body):
        '''deserialize a miner message'''
        message_envelope = self.deserializemessageenvelope(self.safestring(body))
        schema = MinerMessageSchema()
        minermessage_dict = schema.load(message_envelope.bodyjson()).data
        minermessage_entity = schema.make_minermessage(minermessage_dict)
        miner = minermessage_entity.miner
        return miner

    def messagedecodeminerstats(self, body):
        '''deserialize miner stats'''
        message_envelope = self.deserializemessageenvelope(self.safestring(body))
        schema = MinerMessageSchema()
        minermessage_dict = schema.load(message_envelope.bodyjson()).data
        minermessage_entity = schema.make_minermessage(minermessage_dict)
        return minermessage_entity

    def messagedecodeminercommand(self, body):
        '''deserialize  miner command'''
        message_envelope = self.deserializemessageenvelope(self.safestring(body))
        schema = MinerMessageSchema()
        minermessage_dict = schema.load(message_envelope.bodyjson()).data
        minermessage_entity = schema.make_minermessage(minermessage_dict)
        return minermessage_entity

    def messagedecodesensor(self, body):
        '''deserialize sensor value '''
        message_envelope = self.deserializemessageenvelope(self.safestring(body))
        schema = SensorValueSchema()
        #minermessage_dict = schema.load(message_envelope.bodyjson()).data
        entity = schema.load(message_envelope.bodyjson()).data
        return message_envelope, entity


    def createmessageenvelope(self):
        '''create message envelope'''
        return Message(timestamp=datetime.datetime.utcnow(), sender=self.component)

    def serializemessageenvelope(self, msg):
        '''serialize message envelope'''
        return self._schemamsg.dumps(msg).data

    def jsonserialize(self, sch, msg):
        '''serialize a message with schema'''
        return json.dumps(sch.dump(msg))

    def serialize(self, entity):
        '''serialize any entity
        only need schema, message class not needed
        '''
        #for now only handle miner, later add other entities
        schema = MinerSchema()
        return schema.dumps(entity).data

    def serializelist(self, listofentities):
        '''serialize a list of entities'''
        json_list = json.dumps([e.__dict__ for e in listofentities])
        return json_list

    def deserializelistofstrings(self, the_list):
        '''deserialize list of strings into list of miners'''
        results = []
        for item in the_list:
            #thejson = json.loads(self.safestring(item))
            #miner = Miner(**thejson)
            #TODO: the miner here is a Miner but the children are dicts
            miner = self.deserialize(MinerSchema(), self.safestring(item))
            results.append(miner)
        return results

    def deserialize(self, sch, msg):
        '''Output should be entity, not python json object
        msg parameter should be string
        '''
        if msg is None: return None
        return sch.loads(msg).data

    def deserializemessageenvelope(self, body):
        '''serialize message envelope'''
        return self._schemamsg.load(json.loads(self.safestring(body))).data

    def createmessagestats(self, miner, minerstats, minerpool):
        #always save the miner so the next guy can get latest changes
        #todo: should only put if it came from cache
        if miner.store == 'mem':
            self.putminer(miner)
        message = self.createmessageenvelope()
        message = message.make_minerstats(miner, minerstats, minerpool)
        return self.serializemessageenvelope(message)

    def createmessagecommand(self, miner, command):
        '''create message command'''
        if miner.store == 'mem':
            self.putminer(miner)
        message = self.createmessageenvelope()
        message = message.make_minercommand(miner, command)
        return self.serializemessageenvelope(message)

    def messageencode(self, miner):
        '''command is optional, however should convert this call into minercommand'''
        #always save the miner so the next guy can get latest changes
        #todo: should only put if it came from redis
        if miner.store == 'mem':
            self.putminer(miner)
        message = self.createmessageenvelope()
        message = message.make_minerstats(miner, minerstats=None, minerpool=None)
        return self._schemamsg.dumps(message).data

    def alert(self, message):
        '''send alert message'''
        return self.send(QueueName.Q_ALERT, message)

    def send(self, q_name, message):
        '''send message to queue'''
        thequeue = self.makequeue(q_name, self.component)
        success = self.trypublish(thequeue, message)
        self.closequeue(thequeue)
        return success

    def enqueue(self, queuelist):
        '''send a list of queue messages'''
        if queuelist is None:
            return
        if not queuelist.hasentries():
            return
        #todo: group by queuename
        for entry in queuelist.entries:
            self.sendqueueitem(entry)

    def sendqueueitem(self, entry):
        '''send one queue item'''
        #self.logdebug('{0}->{1} {2}'.format(entry.eventtype, entry.queuename, entry.message[:20]))
        if entry.eventtype == 'broadcast':
            thequeue = BroadcastSender(entry.queuename, self.getservice_useroverride(ServiceName.messagebus))
            self.registerqueue(thequeue)
            self.trybroadcast(thequeue, entry.message)
            self.closequeue(thequeue)
        else:
            self.send(entry.queuename, entry.message)

    def take_picture(self, file_name='fullcycle_camera.png'):
        pic = take_picture(file_name, 
                           self.configuration('camera.size'),
                           self.configuration('camera.quality'),
                           self.configuration('camera.brightness'),
                           self.configuration('camera.contrast'))
        return pic

    def store_picture_cache(self, file_name):
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as photofile:
                picdata = photofile.read()
            reading = SensorValue('fullcyclecamera', base64.b64encode(picdata), 'camera')
            #reading.sensor = self.sensor
            #self.sendsensor(reading)
            message = self.createmessageenvelope()
            sensorjson = message.jsonserialize(SensorValueSchema(), reading)
            self.tryputcache(CacheKeys.camera, sensorjson)

    def readtemperature(self):
        try:
            sensor_humid, sensor_temp = readtemperature()
            if sensor_temp is not None:
                reading = SensorValue('fullcycletemp', sensor_temp, 'temperature')
                reading.sensor = self.sensor
                self.sendsensor(reading)
            if sensor_humid is not None:
                reading = SensorValue('fullcyclehumid', sensor_humid, 'humidity')
                reading.sensor = self.sensor
                self.sendsensor(reading)
            return sensor_humid, sensor_temp
        except BaseException as ex:
            self.logexception(ex)
        return None, None

    def sendsensor(self, reading):
        message = self.createmessageenvelope()
        sensorjson = message.jsonserialize(SensorValueSchema(), reading)
        self.sendqueueitem(QueueEntry(QueueName.Q_SENSOR, self.serializemessageenvelope(message.make_any('sensorvalue', sensorjson))))

    def sendtelegrammessage(self, message):
        sendalert(message, self.getservice('telegram'))

    def sendtelegramphoto(self, file_name):
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            sendphoto(file_name, self.getservice('telegram'))

    def getsession(self):
        service = self.getservice(ServiceName.database)
        engine = create_engine(service.connection, echo=False)
        Session = sessionmaker(bind=engine)
        return Session()

    def log_mineractivity(self, minerlog):
        try:
            session = self.getsession()
            session.add(minerlog)
            session.commit()
            return True
        except BaseException as ex:
            self.logexception(ex)
        return False

def main():
    full_cycle = ApplicationService()
    full_cycle.loginfo('Full Cycle was run in a script')
    full_cycle.shutdown()

if __name__ == "__main__":
    main()
