import os
import base64
from helpers.camerahelper import take_picture
from messaging.sensormessages import SensorValueSchema
from domain.sensors import SensorValue
#from backend.fcmservice import BaseService
from backend.fcmcache import CacheKeys
import backend.fcmservice

class CameraService(backend.fcmservice.BaseService):
    #def __init__(self, config, cache):
    #    super(CameraService, config, cache)

    def take_picture(self, file_name='fullcycle_camera.png'):
        pic = take_picture(file_name,
                           self.configuration.get('camera.size'),
                           self.configuration.get('camera.quality'),
                           self.configuration.get('camera.brightness'),
                           self.configuration.get('camera.contrast'))
        return pic

    def store_picture_cache(self, file_name):
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as photofile:
                picdata = photofile.read()
            #picture will be handled like a sensor
            reading = SensorValue('fullcyclecamera', base64.b64encode(picdata), 'camera')
            message = super().createmessageenvelope()
            sensorjson = message.jsonserialize(SensorValueSchema(), reading)
            self.cache.tryputcache(CacheKeys.camera, sensorjson)
