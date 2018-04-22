'''this one pushes to mydevices'''
import time
import sys
import paho.mqtt.client as mqtt
import Adafruit_DHT

print('Waiting 30 seconds in case wireless needs to initialize...')
time.sleep(30) #Sleep to allow wireless to connect before starting MQTT

#TODO: Move to config
USERNAME = "mydevices_name"
PASSWORD = "mydevices_password"
CLIENTID = "mydevices_clientid"

MQTTC = mqtt.Client(client_id=CLIENTID)
MQTTC.username_pw_set(USERNAME, password=PASSWORD)
MQTTC.connect("mqtt.mydevices.com", port=1883, keepalive=60)
MQTTC.loop_start()

TOPIC_TEMP = "v1/" + USERNAME + "/things/" + CLIENTID + "/data/3"
TOPIC_HUMIDITY = "v1/" + USERNAME + "/things/" + CLIENTID + "/data/4"

while True:
    try:
        #pin 2 or 4 = power, pin 6 = gnd, pin 7 = gpio4
        #https://www.raspberrypi.org/documentation/usage/gpio-plus-and-raspi2/README.md
        HUMIDITY22, TEMP22 = Adafruit_DHT.read_retry(22, 4)
        #22 is the sensor type, 4 is the GPIO pin number (not physical pin number)

        if TEMP22 is not None:
            TEMP22 = "temp,c=" + str(TEMP22)
            MQTTC.publish(TOPIC_TEMP, payload=TEMP22, retain=True)
        if HUMIDITY22 is not None:
            HUMIDITY22 = "rel_hum,p=" + str(HUMIDITY22)
            MQTTC.publish(TOPIC_HUMIDITY, payload=HUMIDITY22, retain=True)
        time.sleep(5)
    except (EOFError, SystemExit, KeyboardInterrupt):
        MQTTC.disconnect()
        sys.exit()
