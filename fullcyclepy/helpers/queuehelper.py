'''messagebug (queue) related functions'''
import pika

class QueueName:
    """Known standard queue names
    You may be able to define and use other queue names
    but you're on your own
    """
    Q_DUMMY = 'dummy'
    Q_COMPONENT = 'component'
    Q_LOG = 'log'
    Q_PROVISION = 'provision'
    Q_SWITCH = 'switch'
    Q_RESTART = 'restart'
    Q_ALERT = 'alert'
    Q_DISCOVER = 'discover'
    Q_DISCOVERED = 'discovered'
    Q_MONITOR = 'monitor'
    Q_MONITORMINER = 'monitorminer'
    Q_SHUTDOWN = 'shutdown'
    Q_OFFLINE = 'offline'
    Q_ONLINE = 'online'
    Q_STATISTICSUPDATED = 'statisticsupdated'
    Q_POOLCONFIGURATIONCHANGED = 'poolconfigurationchanged'
    Q_CLOUDPULL = 'cloudpull'
    Q_EMAIL = 'email'
    Q_SENSOR = 'sensor'
    Q_UPDATEWEB = 'updateweb'
    Q_SAVE = 'save'

    def isvalidqname(self, queue_name):
        #pylint: disable=too-many-return-statements
        if queue_name == self.Q_COMPONENT:
            return True
        if queue_name == self.Q_LOG:
            return True
        if queue_name == self.Q_PROVISION:
            return True
        if queue_name == self.Q_SWITCH:
            return True
        if queue_name == self.Q_RESTART:
            return True
        if queue_name == self.Q_ALERT:
            return True
        if queue_name == self.Q_DISCOVER:
            return True
        if queue_name == self.Q_DISCOVERED:
            return True
        if queue_name == self.Q_MONITOR:
            return True
        if queue_name == self.Q_MONITORMINER:
            return True
        if queue_name == self.Q_SHUTDOWN:
            return True
        if queue_name == self.Q_OFFLINE:
            return True
        if queue_name == self.Q_ONLINE:
            return True
        if queue_name == self.Q_CLOUDPULL:
            return True
        if queue_name == self.Q_EMAIL:
            return True
        if queue_name == self.Q_SENSOR:
            return True
        if queue_name == self.Q_UPDATEWEB:
            return True
        return False


class QueueType:
    broadcast = 'broadcast'
    publish = 'publish'


class QueueEntry(object):
    '''An entry that will go into a queue'''
    def __init__(self, queuename, message, eventtype=QueueType.publish):
        self.queuename = queuename
        self.eventtype = eventtype
        self.message = message


class QueueEntries(object):
    '''a list of queue entries'''
    def __init__(self):
        self.entries = []

    def add(self, queuename, message):
        self.entries.append(QueueEntry(queuename, message, QueueType.publish))

    def addbroadcast(self, queuename, message):
        self.entries.append(QueueEntry(queuename, message, QueueType.broadcast))

    def addalert(self, message):
        self.addbroadcast(QueueName.Q_ALERT, message)

    def hasentries(self):
        if self.entries is None:
            return 0
        return len(self.entries)


class Queue:
    """
    Wrapper around a rabbitmq queue
    """
    queue_name = None
    _connection = None
    channel = None
    state = None
    _userlogin = None

    def __init__(self, queueName, servicelogin):
        self.queue_name = queueName
        self._servicelogin = servicelogin
        self._userlogin = self._servicelogin.user
        if self._userlogin is None:
            self._userlogin = 'fullcycle'
        self.initialize(queueName)

    def getparameters(self):
        credentials = pika.PlainCredentials(self._userlogin, self._servicelogin.password)
        parameters = pika.ConnectionParameters(self._servicelogin.host, self._servicelogin.port, '/', credentials)
        return parameters

    def initialize(self, name):
        '''init'''
        self.setupchannel()
        self.declare(name)

    def setupchannel(self):
        '''create the channel'''
        self._connection = pika.BlockingConnection(self.getparameters())
        self.channel = self._connection.channel()

    def declare(self, name):
        """Creates the queue"""
        self.state = self.channel.queue_declare(queue=name)

    def publish(self, msg, exchange=''):
        """Publishes message for one consumer"""
        if self.channel != None:
            self.channel.basic_publish(exchange=exchange, routing_key=self.queue_name, body=msg)

    def subscribe(self, callback, no_acknowledge=True, prefetch_count=1):
        """Consumes messages from one queue"""
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(callback, queue=self.queue_name, no_ack=no_acknowledge)

    def listen(self):
        '''listen to queue'''
        self.channel.start_consuming()

    def sleep(self, duration):
        '''call this periodically so the connection does not time out'''
        self._connection.sleep(duration)

    def getmessage(self, no_acknowledge=True):
        """if not listening then you can get message in a loop"""
        queue_empty = self.state.method.message_count == 0
        if not queue_empty:
            return self.channel.basic_get(self.queue_name, no_ack=no_acknowledge)
        return (None, None, None)

    def acknowledge(self, delivery_tag):
        '''acknowledge that message was processed'''
        self.channel.basic_ack(delivery_tag)

    def reject(self, delivery_tag):
        '''tell queue that message was not processed'''
        self.channel.basic_nack(delivery_tag)

    def close(self):
        """close the queue"""
        if self.channel != None:
            self.channel.close()
            self.channel = None
            self._connection = None
            self.state = None

class BroadcastBase(Queue):
    '''a queue for broadcasting messages to multiple recipients
    todo: should be abstract'''
    _exchangename = None
    _exchangetype = None

    def initialize(self, name):
        '''init'''
        self.setupchannel()
        self.setupbroadcast(name)
        #do not need to declare when sending!
        self.declare(name)

    def setupexchange(self, name, exchange_type):
        '''set up the exchange for broadcasting'''
        self._exchangename = name
        self._exchangetype = exchange_type
        self.channel.exchange_declare(exchange=name, exchange_type=exchange_type)
        return self

    def setupbroadcast(self, name):
        '''set up the exchange for broadcasting'''
        return self.setupexchange(name, 'fanout')

class BroadcastSender(BroadcastBase):
    def initialize(self, name):
        '''init'''
        self.setupchannel()
        self.setupbroadcast(name)
        #no declare when sending

    def broadcast(self, msg):
        '''broadcast a message to anyone that is listening'''
        if self.channel != None:
            self.channel.basic_publish(exchange=self._exchangename, routing_key='', body=msg)

class BroadcastListener(BroadcastBase):

    def initialize(self, name):
        '''init'''
        self.setupchannel()
        self.setupbroadcast(name)
        #only need to declare channel when listening
        self.declarechannel()

    def declarechannel(self):
        '''declare the channel'''
        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=self._exchangename, queue=self.queue_name)
