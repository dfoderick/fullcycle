
import backend.fcmutils as utils
import backend.fcmservice
from backend.fcmcache import CacheKeys
from domain.sensors import Sensor, SensorValue

class SensorService(backend.fcmservice.BaseService):
    def __init__(self, config, cache):
        super().__init__(config, cache)
        self.sensor = Sensor('controller', 'DHT22', 'controller')

    def knownsensors(self):
        dknownsensors = self.__cache.gethashset(CacheKeys.knownsensors)
        if dknownsensors is not None and dknownsensors:
            return utils.deserializelist_withschema(SensorValueSchema(), list(dknownsensors.values()))
        return None

    def addknownsensor(self, sensorvalue):
        val = utils.jsonserialize(SensorValueSchema(), sensorvalue)
        self.__cache.putinhashset(CacheKeys.knownsensors, sensorvalue.sensorid, val)

