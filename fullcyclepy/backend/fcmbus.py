import pika
from helpers.queuehelper import QueueName

class Bus:
    _connection = None
    _durable = False

    def __init__(self, servicelogin):
        self._servicelogin = servicelogin
        self._userlogin = self._servicelogin.user
        if self._userlogin is None:
            self._userlogin = 'fullcycle'
    @classmethod
    def get_queue_name(self, queue_name):
        name_of_q = queue_name
        if isinstance(queue_name, QueueName):
            name_of_q = QueueName.value(queue_name)
        return name_of_q

    def connection(self):
        if not self._connection:
            credentials = pika.PlainCredentials(self._userlogin, self._servicelogin.password)
            parameters = pika.ConnectionParameters(self._servicelogin.host, self._servicelogin.port, '/', credentials)
            self._connection = pika.BlockingConnection(parameters)
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()

    def sleep(self, seconds):
        if self._connection:
            self._connection.sleep(seconds)

    def publish(self, queue_name, msg, exchange=''):
        """Publishes message on new channel"""
        localchannel = self.connection().channel()
        localchannel.queue_declare(queue=Bus.get_queue_name(queue_name), durable=self._durable)
        localchannel.basic_publish(exchange=exchange, routing_key=Bus.get_queue_name(queue_name), body=msg)
        localchannel.close()

    def broadcast(self, exchange_name, msg):
        '''broadcast a message to anyone that is listening'''
        localchannel = self.connection().channel()
        localchannel.exchange_declare(exchange=Bus.get_queue_name(exchange_name), exchange_type='fanout')
        localchannel.basic_publish(exchange=Bus.get_queue_name(exchange_name), routing_key='', body=msg)
        localchannel.close()

    def subscribe(self, name, callback, no_acknowledge=True, prefetch_count=1):
        """basic subscribe messages from one queue
        remember to listen to channel to get messages
        """
        localchannel = self.connection().channel()
        localchannel.queue_declare(queue=Bus.get_queue_name(name))
        localchannel.basic_qos(prefetch_count=prefetch_count)
        localchannel.basic_consume(callback, queue=Bus.get_queue_name(name), no_ack=no_acknowledge)
        return localchannel

    def subscribe_broadcast(self, name, callback, no_acknowledge=True, prefetch_count=1):
        """Consumes messages from one queue"""
        localchannel = self.connection().channel()
        localchannel.exchange_declare(exchange=Bus.get_queue_name(name), exchange_type='fanout')

        result = localchannel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        localchannel.queue_bind(exchange=Bus.get_queue_name(name), queue=queue_name)

        localchannel.basic_qos(prefetch_count=prefetch_count)
        localchannel.basic_consume(callback, queue=queue_name, no_ack=no_acknowledge)
        return localchannel

    def listen(self, channel):
        '''listen to queue. this is a blocking call'''
        channel.start_consuming()

    def acknowledge(self, channel, delivery_tag):
        '''acknowledge that message was processed'''
        channel.basic_ack(delivery_tag)

    def reject(self, channel, delivery_tag):
        '''tell queue that message was not processed'''
        channel.basic_nack(delivery_tag)
