'''
    A test program that pushes monitoring messages onto the queue
    A stress tester for monitoring
    when_monitorminer.py should be running to process the messages
'''

from helpers.queuehelper import QueueName, QueueEntries
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)
MINERS = APP.miners()

CNT = 1
while CNT < 2000:
    ENTRIES = QueueEntries()
    for miner in MINERS:
        ENTRIES.add(QueueName.Q_MONITORMINER, APP.messageencode(miner))
    APP.enqueue(ENTRIES)
    print('sent {} messages'.format(len(ENTRIES.entries)))
    CNT += 1
