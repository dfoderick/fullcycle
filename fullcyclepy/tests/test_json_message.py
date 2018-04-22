'''# test json message format
# scenarios:
# - Miner with miner stats
# - Miner with command
# - command by itself
# - sensor
'''
import unittest
import datetime
#from marshmallow import pprint
from domain.mining import Miner, MinerInfo, MinerCurrentPool, MinerStatistics
#from domain.sensors import SensorValue
from messaging.messages import MinerSchema

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

if __name__ == '__main__':
    unittest.main()
