'''http://emmanuel-klinger.net/distributed-task-queues-for-machine-learning-in-python-celery-rabbitmq-redis.html'''

import pika
import time
from backend.fcmapp import ApplicationService, ServiceName

DURABLE = False
APP = ApplicationService()

connection = APP.bus.connection
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=DURABLE)
channel.basic_qos(prefetch_count=1)

N = 100000
start = time.time()
for k in range(N):
    channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=str((1, k)),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
send_finish = time.time()

channelr = connection.channel()
channelr.queue_declare(queue='result_queue', durable=DURABLE)

k = 0
def callback(ch, method, properties, body):
    global k
    ch.basic_ack(delivery_tag = method.delivery_tag)
    if k == N-1:
        end = time.time()
        print("rabbit", send_finish - start,  end - start)
    k += 1

channelr.basic_qos(prefetch_count=1)
channelr.basic_consume(callback, queue='result_queue')
channelr.start_consuming()
