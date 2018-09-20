'''# test json message format
# scenarios:
# - Miner with miner stats
# - Miner with command
# - command by itself
# - sensor
'''
import unittest
import datetime
import domain.minerstatistics
from domain.mining import Miner, MinerStatus, MinerInfo, MinerCurrentPool, MinerCommand, Pool, AvailablePool
from domain.sensors import SensorValue, Sensor
import messaging.messages
import messaging.sensormessages
import messaging.schema
from messaging.sensormessages import SensorValueSchema
from backend.fcmapp import ApplicationService
import backend.fcmutils as utils

class TestSerialization(unittest.TestCase):
    def test_sensors(self):
        msg = messaging.sensormessages.SensorValueMessage('', '', '')
        self.assertTrue(msg)
        msg = messaging.sensormessages.SensorMessage('', '', '')
        self.assertTrue(msg)

    def test_messages(self):
        msg = messaging.messages.MinerCommandMessage()
        self.assertTrue(msg)

    def test_minercommand(self):
        sch = messaging.schema.MinerCommandSchema()
        cmd = MinerCommand()
        j = sch.dumps(cmd).data
        recommand = sch.loads(j).data
        self.assertTrue(isinstance(recommand, MinerCommand))

    def test_minermessage(self):
        sch = messaging.messages.MinerMessageSchema()
        entity = messaging.messages.MinerMessage(Miner('test'))
        entity.command = MinerCommand('test','test')
        entity.minerpool = MinerCurrentPool(entity.miner, 'test pool', 'test worker', allpools={})
        entity.minerstats = domain.minerstatistics.MinerStatistics(entity.miner, datetime.datetime.utcnow(), 0, 1, 0, 99, 98, 97, 123, '', '', '')
        j = sch.dumps(entity).data
        reentity = sch.loads(j).data
        self.assertTrue(isinstance(reentity, messaging.messages.MinerMessage))

    def test_pool(self):
        sch = messaging.schema.PoolSchema()
        entity = Pool('', '', '', '', 1, '')
        j = sch.dumps(entity).data
        reentity = sch.loads(j).data
        self.assertTrue(isinstance(reentity, Pool))

    def test_availablepool(self):
        sch = messaging.schema.AvailablePoolSchema()
        entity = AvailablePool('type')
        j = sch.dumps(entity).data
        reentity = sch.loads(j).data
        self.assertTrue(isinstance(reentity, AvailablePool))

    def test_minerserialization(self):
        sch = messaging.messages.MinerSchema()
        miner = Miner('test')
        miner.status = MinerStatus.Offline
        miner.status = MinerStatus.Online
        miner.minerinfo = MinerInfo('Antminer S9', '123')
        miner.minerpool = MinerCurrentPool(miner, 'test pool', 'test worker', allpools={})
        miner.minerpool.poolname = 'unittest'
        miner.minerstats = domain.minerstatistics.MinerStatistics(miner, datetime.datetime.utcnow(), 0, 1, 0, 99, 98, 97, 123, '', '', '')
        miner.minerstats.boardstatus1 = 'o'
        miner.minerstats.boardstatus2 = 'oo'
        miner.minerstats.boardstatus3 = 'ooo'
        miner.location = 'unittest'
        miner.in_service_date = datetime.datetime.today().replace(microsecond=0)
        jminer = sch.dumps(miner).data

        #rehydrate miner
        reminer = messaging.messages.MinerSchema().loads(jminer).data
        self.assertTrue(isinstance(reminer.minerinfo, MinerInfo))
        self.assertTrue(isinstance(reminer.minerpool, MinerCurrentPool))
        self.assertTrue(reminer.minerpool.poolname == 'unittest')
        self.assertTrue(isinstance(reminer.minerstats, domain.minerstatistics.MinerStatistics))
        self.assertTrue(reminer.laststatuschanged)
        self.assertTrue(reminer.minerstats.boardstatus1 == 'o')
        self.assertTrue(reminer.minerstats.boardstatus2 == 'oo')
        self.assertTrue(reminer.minerstats.boardstatus3 == 'ooo')
        self.assertTrue(reminer.location == miner.location)
        self.assertTrue(reminer.in_service_date == miner.in_service_date)

    def test_miner_deserialize(self):
        miner = Miner("unittest", None, "", "unitip", "unitport", "", "")
        jminer = utils.serialize(miner, messaging.messages.MinerSchema())
        reminer = utils.deserialize(messaging.messages.MinerSchema(), jminer) #().loads(jminer).data
        self.assertTrue(isinstance(reminer, Miner), "object from MinerSchema should be a miner")

    def test_sensorvalue_serialization(self):
        '''on windows the deserialization seems to lose the fractions of seconds
        so this test is only for seconds'''
        sch = SensorValueSchema()
        sensorvalue = SensorValue('testid', '99.9', 'temperature')
        sensorvalue.sensor = Sensor('testid', 'temperature', 'controller')
        sensortime = sensorvalue.sensortime
        jsensor = sch.dumps(sensorvalue).data

        #rehydrate sensor
        resensor = SensorValueSchema().loads(jsensor).data
        self.assertTrue(isinstance(resensor, SensorValue))
        self.assertTrue(resensor.sensortime.day == sensortime.day)
        self.assertTrue(resensor.sensortime.hour == sensortime.hour)
        self.assertTrue(resensor.sensortime.minute == sensortime.minute)
        self.assertTrue(resensor.sensortime.second == sensortime.second)
        self.assertTrue(isinstance(resensor.sensor, Sensor))
        self.assertTrue(resensor.sensorid == resensor.sensor.sensorid)

    def test_config_serialization(self):
        sch = messaging.messages.ConfigurationMessageSchema()
        msg = messaging.messages.ConfigurationMessage('save', '', 'pool', {"configuration_message_id":"name"}, [{"name":"my pool"}])
        jconfig = sch.dumps(msg).data
        reconfig = sch.loads(jconfig).data
        self.assertTrue(isinstance(reconfig, messaging.messages.ConfigurationMessage))
        self.assertTrue(isinstance(reconfig.command, str))
        self.assertTrue(isinstance(reconfig.parameter, str))
        self.assertTrue(isinstance(reconfig.configuration_message_id, dict))
        self.assertTrue(isinstance(reconfig.values, list))

    def test_message_inapp(self):
        app = ApplicationService(component='test')
        values = '{"version":"1.1","sender":"fullcyclereact","type":"configuration","timestamp":"2018-09-16T07:18:34.431Z","body":"{\\"command\\":\\"save\\",\\"parameter\\":\\"\\",\\"id\\":\\"unknown\\",\\"entity\\":\\"miner\\",\\"values\\":[{\\"name\\":\\"S9102\\"},{\\"ipaddress\\":\\"test.com\\"},{\\"port\\":\\"4102\\"},{\\"location\\":\\"222\\"},{\\"in_service_date\\":null}]}"}'
        msg = app.messagedecode_configuration(values)
        self.assertTrue(isinstance(msg, messaging.messages.ConfigurationMessage))
        self.assertTrue(msg.entity == 'miner')
        miner = Miner.create(msg.values)
        self.assertTrue(miner.name == "S9102")

if __name__ == '__main__':
    unittest.main()
