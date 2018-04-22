'''interface to mydevices'''
import paho.mqtt.client as mqtt

#configuration section for Cayenne Mydevices
MQTT_SERVER = "mqtt.mydevices.com"
MQTT_PORT = 1883

def topic(index, miner):
    topik = "v1/" + miner.username + "/things/" + miner.clientid + "/data/"+index
    return topik

def startdevice(clientid, uname, pwd):
    mqttc = mqtt.Client(client_id=clientid)
    mqttc.username_pw_set(uname, password=pwd)
    mqttc.connect(MQTT_SERVER, port=MQTT_PORT, keepalive=120)
    mqttc.loop_start()
    return mqttc
