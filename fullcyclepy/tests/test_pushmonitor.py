'''
    A test program that pushes monitoring messages onto the queue
    A stress tester for monitoring
    when_monitorminer.py should be running to process the messages
'''

from helpers.queuehelper import QueueName, QueueEntries
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)
MINERS = APP.miners()

cnt = 1
while cnt < 1000:
    entries = QueueEntries()
    for miner in MINERS:
        entries.add(QueueName.Q_MONITORMINER, APP.messageencode(miner))
    APP.enqueue(entries)
    print('sent {} messages'.format(len(entries.entries)))
    cnt += 1

