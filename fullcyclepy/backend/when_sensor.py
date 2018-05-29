'''what to do when a sensor reading is broadcast'''
from helpers.queuehelper import QueueName
from fcmapp import Component

SENSOR = Component('fullcycle')

def when_sensor(channel, method, properties, body):
    '''when there is a sensor reading'''
    try:
        print("[{0}] Received sensor reading".format(SENSOR.app.now()))
        message, sensorvalue = SENSOR.app.messagedecodesensor(body)
        dosensor(message, sensorvalue)
    except Exception as ex:
        SENSOR.app.logexception(ex)

def dosensor(message, sensorvalue):
    '''put the sensor in cache'''
    SENSOR.app.addknownsensor(sensorvalue)

def main():
    SENSOR.listeningqueue = SENSOR.app.listen_to_broadcast(QueueName.Q_SENSOR, when_sensor)

if __name__ == "__main__":
    main()
