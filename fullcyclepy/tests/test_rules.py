'''test rules'''
import unittest
import datetime
from domain.mining import Miner, MinerInfo, MinerStatistics
from domain.miningrules import RuleParameters, MinerStatisticsRule, BrokenRule

class TestRules(unittest.TestCase):
    def setUp(self):
        '''create test miner'''
        self.minerinfo = MinerInfo('Antminer S9', '')
        self.miner = Miner('Test', 'Online', 'Antminer S9', '', '', '', '', '', '', '',
                           lastmonitor=None, offlinecount=0, defaultpool='', minerinfo=self.minerinfo)

        self.minerstats = MinerStatistics(self.miner, datetime.datetime.utcnow(), 3, currenthash=9999,
                                          controllertemp=0, tempboard1=0, tempboard2=0, tempboard3=0)

    def test_int_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)
        self.assertTrue(rules.hasreading_num(params.controllertemplimit))

    def test_float_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 49.9, 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)
        self.assertTrue(rules.hasreading_num(params.controllertemplimit))

    def test_string_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, '', 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)
        self.assertFalse(rules.hasreading_num(params.controllertemplimit))

    def test_lowhash(self):
        '''test low hash condition'''
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)

        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertTrue(len(rules.brokenrules) > 0)

    def test_board_high_temp(self):
        '''test when controller temp is high on miner'''
        self.minerstats.tempboard1 = 101
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)

        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertTrue(len(rules.brokenrules) > 0)

    def test_board_high_temp_reset(self):
        '''test when controller temp is high on miner'''
        self.minerstats.tempboard1 = 150
        self.minerstats.elapsed = (60 * 10) + 1
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10, maxtempreset=120)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)

        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertTrue(rules.has_reboot_rule())

    def test_controller_high_temp_reset_null(self):
        '''test when controller temp is high on miner. no reset'''
        self.minerstats.controllertemp = 101
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10, maxtempreset = None)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)

        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertFalse(rules.has_reboot_rule())


    def test_only_one_reset(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner,'restart',''))
        rules.addbrokenrule(BrokenRule(self.miner,'restart',''))
        self.assertTrue(len(rules.brokenrules) == 1)

    def test_only_one_reboot(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner,'restart','reboot'))
        rules.addbrokenrule(BrokenRule(self.miner,'restart','reboot'))
        self.assertTrue(len(rules.brokenrules) == 1)

    def test_reset_leaves_reboot(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner,'restart','reboot'))
        rules.addbrokenrule(BrokenRule(self.miner,'restart',''))
        self.assertTrue(len(rules.brokenrules) == 1)
        self.assertTrue(rules.brokenrules[0].parameter == 'reboot')

if __name__ == '__main__':
    unittest.main()
