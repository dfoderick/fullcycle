'''http://emmanuel-klinger.net/distributed-task-queues-for-machine-learning-in-python-celery-rabbitmq-redis.html'''

import pika
from backend.fcmapp import ApplicationService

DURABLE = False
APP = ApplicationService()

CONNECTION = APP.bus.connection()

CHANNEL = CONNECTION.channel()
CHANNEL.queue_declare(queue='task_queue', durable=DURABLE)

CHANNELR = CONNECTION.channel()
CHANNELR.queue_declare(queue='result_queue', durable=DURABLE)

def callback(chan, method, properties, body):
    print(body)
    vara, varb = list(map(int, body.decode()[1:-1].split(",")))
    res = str(vara + varb)
    CHANNELR.basic_publish(exchange='',
                           routing_key='result_queue',
                           body=res,
                           properties=pika.BasicProperties(
                               delivery_mode=2, ))
    chan.basic_ack(delivery_tag=method.delivery_tag)

CHANNEL.basic_qos(prefetch_count=1)
CHANNEL.basic_consume(callback, queue='task_queue')

CHANNEL.start_consuming()
