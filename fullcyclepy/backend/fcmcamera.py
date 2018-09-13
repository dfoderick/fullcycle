
import backend.fcmservice
#from backend.fcmservice import BaseService
from helpers.camerahelper import take_picture
from domain.sensors import SensorValue

class CameraService(backend.fcmservice.BaseService):
    #def __init__(self, config, cache):
    #    super(CameraService, config, cache)

    def take_picture(self, file_name='fullcycle_camera.png'):
        pic = take_picture(file_name,
                           super().configuration.get('camera.size'),
                           super().configuration.get('camera.quality'),
                           super().configuration.get('camera.brightness'),
                           super().configuration.get('camera.contrast'))
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



