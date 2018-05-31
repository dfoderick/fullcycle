'''http://emmanuel-klinger.net/distributed-task-queues-for-machine-learning-in-python-celery-rabbitmq-redis.html'''

import time
import pika
from backend.fcmapp import ApplicationService

DURABLE = False
APP = ApplicationService()

CONNECTION = APP.bus.connection()
CHANNEL = CONNECTION.channel()
CHANNEL.queue_declare(queue='task_queue', durable=DURABLE)
CHANNEL.basic_qos(prefetch_count=1)

N = 100000
START = time.time()
for k in range(N):
    CHANNEL.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=str((1, k)),
                          properties=pika.BasicProperties(delivery_mode=2, ))
SEND_FINISH = time.time()

CHANNELR = CONNECTION.channel()
CHANNELR.queue_declare(queue='result_queue', durable=DURABLE)

k = 0
def callback(chan, method, properties, body):
    global k
    chan.basic_ack(delivery_tag=method.delivery_tag)
    if k == N-1:
        end = time.time()
        print("rabbit", SEND_FINISH - START, end - START)
    k += 1

CHANNELR.basic_qos(prefetch_count=1)
CHANNELR.basic_consume(callback, queue='result_queue')
CHANNELR.start_consuming()
