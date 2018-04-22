'''sensor messages and schema'''
from marshmallow import Schema, fields, post_load
from domain.sensors import Sensor, SensorValue

class SensorValueMessage(object):
    """Sensor data in a message"""
    def __init__(self, sensorid, value, sensor_type):
        self.sensorid = sensorid
        self.value = value
        self.type = sensor_type

class SensorMessage(object):
    """Sensor message"""
    def __init__(self, sensorid, sensor_type, location):
        self.sensorid = sensorid
        self.type = sensor_type
        self.location = location

class SensorSchema(Schema):
    '''schema for sensor'''
    sensorid = fields.Str()
    sensortype = fields.Str()
    location = fields.Str()

    @post_load
    def make_sensor(self, data):
        '''reconstitute sensor'''
        entity = Sensor(sensorid=data['sensorid'], sensortype=data['sensortype'],
                        location=data['location'])
        return entity

class SensorValueSchema(Schema):
    '''serialized version of sensor value'''
    sensorid = fields.Str()
    value = fields.Str()
    valuetype = fields.Str()

    @post_load
    def make_sensorvalue(self, data):
        '''reconstitute sensorvalue'''
        entity = SensorValue(sensorid=data['sensorid'], value=data['value'],
                             valuetype=data['valuetype'])
        return entity
