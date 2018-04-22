'''what to do when a sensor is read'''
#import paho.mqtt.client as mqtt
import sys
#import jsonpickle
from helpers import mydeviceshelper
from helpers.queuehelper import QueueName, BroadcastListener
from fcmapp import ApplicationService

APP = ApplicationService(component='sensor')

def shutdown():
    '''#TODO: make this get call on app shutdown'''
    print('Shutting down...')
    for miner in MINERS:
        DEVICES[miner.clientid].disconnect()
    QUEUE.close()
    sys.exit()

MINERS = APP.miners()
print("{0} miners configured".format(len(MINERS)))

DEVICES = dict()
for MINER in MINERS:
    DEVICES[MINER.clientid] = mydeviceshelper.startdevice(MINER.clientid, MINER.username, MINER.password)

def when_miner_stats_updated(channel, method, properties, body):
    '''when miner statistics have been read'''
    print("[{0}] Received miner stats".format(APP.now()))
    msg = APP.messagedecodeminerstats(body)
    dopushtomydevices(msg.miner, msg.minerstats, msg.minerpool)

def dopushtomydevices(myminer, minerstats, minerpool):
    '''send device values to mydevices'''
    if minerstats.currenthash is not None:
        hashvalue = "freq,hz=" + str(minerstats.currenthash)
        DEVICES[myminer.clientid].publish(mydeviceshelper.topic("1", myminer), payload=hashvalue, retain=True)
    if minerstats.tempboard1 is not None:
        temp1value = "temp,c=" + str(minerstats.tempboard1)
        DEVICES[myminer.clientid].publish(mydeviceshelper.topic("2", myminer), payload=temp1value, retain=True)
    if minerstats.tempboard2 is not None:
        temp2value = "temp,c=" + str(minerstats.tempboard2)
        DEVICES[myminer.clientid].publish(mydeviceshelper.topic("3", myminer), payload=temp2value, retain=True)
    if minerstats.tempboard3 is not None:
        temp3value = "temp,c=" + str(minerstats.tempboard3)
        DEVICES[myminer.clientid].publish(mydeviceshelper.topic("4", myminer), payload=temp3value, retain=True)
    print("Pushed to mydevices {0}".format(myminer.name))

QUEUE = BroadcastListener(QueueName.Q_STATISTICSUPDATED, APP.component)

print('Waiting for statisticsupdated on {0}. To exit press CTRL+C'.format(QUEUE.queue_name))

QUEUE.subscribe(when_miner_stats_updated)

APP.listen(QUEUE)
