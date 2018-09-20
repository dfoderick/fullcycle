
import backend.fcmutils as utils
import backend.fcmservice
from backend.fcmcache import CacheKeys
from domain.sensors import Sensor, SensorValue
from messaging.sensormessages import SensorValueSchema
from helpers.temperaturehelper import readtemperature

class SensorService(backend.fcmservice.BaseService):
    def __init__(self, config, cache):
        super().__init__(config, cache)
        self.sensor = Sensor('controller', 'DHT22', 'controller')

    def knownsensors(self):
        dknownsensors = self.cache.gethashset(CacheKeys.knownsensors)
        if dknownsensors is not None and dknownsensors:
            return utils.deserializelist_withschema(SensorValueSchema(), list(dknownsensors.values()))
        return None

    def addknownsensor(self, sensorvalue):
        val = utils.jsonserialize(SensorValueSchema(), sensorvalue)
        self.cache.putinhashset(CacheKeys.knownsensors, sensorvalue.sensorid, val)

    def readtemperature(self):
        temperature_reading = humidity_reading = None
        try:
            sensor_humid, sensor_temp = readtemperature()
            if sensor_temp is not None:
                temperature_reading = SensorValue('fullcycletemp', sensor_temp, 'temperature')
                temperature_reading.sensor = self.sensor
            if sensor_humid is not None:
                humidity_reading = SensorValue('fullcyclehumid', sensor_humid, 'humidity')
                humidity_reading.sensor = self.sensor
        except BaseException: # as ex:
            #self.logexception(ex)
            #todo: reenable
            pass
        return temperature_reading, humidity_reading
