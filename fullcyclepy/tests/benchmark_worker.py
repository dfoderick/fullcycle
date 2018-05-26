'''http://emmanuel-klinger.net/distributed-task-queues-for-machine-learning-in-python-celery-rabbitmq-redis.html'''

import pika
import time
from backend.fcmapp import ApplicationService, ServiceName

DURABLE = False
APP = ApplicationService()

connection = APP.bus.connection

channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=DURABLE)

channelr = connection.channel()
channelr.queue_declare(queue='result_queue', durable=DURABLE)

def callback(ch, method, properties, body):
    print(body)
    a, b = list(map(int,body.decode()[1:-1].split(",")))
    res = str(a+b)
    channelr.basic_publish(exchange='',
                      routing_key='result_queue',
                      body=res,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='task_queue')

channel.start_consuming()
