'''what to do when a sensor reading is broadcast'''
from helpers.queuehelper import QueueName
from fcmapp import Component

SENSOR = Component('fullcycle')

def when_sensor(channel, method, properties, body):
    '''when there is a sensor reading'''
    try:
        print("[{0}] Received request to send telegram".format(ALERT.app.now()))
        message = SENSOR.app.messagedecodesensor(body)
        dosensor(message)
    except Exception as ex:
        SENSOR.app.logexception(ex)

def dosensor(sensormessage):
    '''put the sensor in cache'''
    memsensor = SENSOR.deserialize(SensorValueSchema(), SENSOR.safestring(sensormessage.body))

    sensorvalue = sensormessage.body
    SENSOR.app.addknownsensor(sensorvalue)

def main():
    SENSOR.listeningqueue = ALERT.app.subscribe_and_listen(QueueName.Q_ALERT, when_alert)

if __name__ == "__main__":
    main()

