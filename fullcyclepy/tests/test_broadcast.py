'''test broadcast'''
from helpers.queuehelper import BroadcastSender, QueueName
#from messaging.messages import *
#from domain import mining, rep
from backend.fcmapp import ApplicationService, ServiceName

APP = ApplicationService()

QBROAD = BroadcastSender(QueueName.Q_LOG, APP.getservice(ServiceName.messagebus))
QBROAD.broadcast('{0} WORKING! test_broadcast {1}'.format(APP.now(), QBROAD.queue_name))
QBROAD.close()
