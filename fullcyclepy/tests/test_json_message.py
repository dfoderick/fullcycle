'''# test json message format
# scenarios:
# - Miner with miner stats
# - Miner with command
# - command by itself
# - sensor
'''
import unittest
import datetime
from domain.mining import Miner, MinerInfo, MinerCurrentPool, MinerStatistics
from domain.sensors import SensorValue, Sensor
from messaging.messages import MinerSchema
from messaging.sensormessages import SensorValueMessage, SensorValueSchema

class TestSerialization(unittest.TestCase):
    def test_minerserialization(self):
        sch = MinerSchema()
        miner = Miner('test')
        miner.minerinfo = MinerInfo('Antminer S9', '123')
        miner.minerpool = MinerCurrentPool(miner, 'test pool', 'test worker', allpools={})
        miner.minerpool.poolname = 'unittest'
        miner.minerstats = MinerStatistics(miner, datetime.datetime.utcnow(), 0, 1, 0, 99, 98, 97, 123, '', '', '')
        jminer = sch.dumps(miner).data

        #rehydrate miner
        reminer = MinerSchema().loads(jminer).data
        self.assertTrue(isinstance(reminer.minerinfo, MinerInfo))
        self.assertTrue(isinstance(reminer.minerpool, MinerCurrentPool))
        self.assertTrue(reminer.minerpool.poolname == 'unittest')
        self.assertTrue(isinstance(reminer.minerstats, MinerStatistics))

    def test_sensorvalue_serialization(self):
        sch = SensorValueSchema()
        sensorvalue = SensorValue('testid','99.9','temperature')
        sensorvalue.sensor = Sensor('testid','temperature','controller')
        jsensor = sch.dumps(sensorvalue).data

        #rehydrate sensor
        resensor = SensorValueSchema().loads(jsensor).data
        self.assertTrue(isinstance(resensor, SensorValue))
        self.assertTrue(isinstance(resensor.sensor, Sensor))
        self.assertTrue(resensor.sensorid == resensor.sensor.sensorid)

if __name__ == '__main__':
    unittest.main()
