'''test rules'''
import unittest
import datetime
import domain.minerstatistics
from domain.mining import Miner, MinerInfo
from domain.miningrules import RuleParameters, MinerStatisticsRule, BrokenRule

class TestRules(unittest.TestCase):
    def setUp(self):
        '''create test miner'''
        self.minerinfo = MinerInfo('Antminer S9', '')
        self.miner = Miner('Test', 'Online', 'Antminer S9', '', '', '', '', '', '', '',
                           lastmonitor=None, offlinecount=0, defaultpool='', minerinfo=self.minerinfo)

        self.minerstats = domain.minerstatistics.MinerStatistics(self.miner, datetime.datetime.utcnow(), 3, currenthash=9999,
                                          controllertemp=0, tempboard1=0, tempboard2=0, tempboard3=0)

    def test_int_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10)
        self.assertTrue(MinerStatisticsRule.hasreading_num(params.controllertemplimit))

    def test_float_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 49.9, 55, 60*10)
        self.assertTrue(MinerStatisticsRule.hasreading_num(params.controllertemplimit))

    def test_string_has_reading(self):
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, '', 55, 60*10)
        self.assertFalse(MinerStatisticsRule.hasreading_num(params.controllertemplimit))

    def test_incompatable_minertype(self):
        params = RuleParameters('notthesameminertype', 10000, 40, 55, 60*10)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)
        isbroken = rules.isbroken()
        self.assertFalse(isbroken)

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

    def test_high_temp_reset_null(self):
        '''test when controller temp is high on miner. no reset'''
        self.minerstats.controllertemp = 101
        params = RuleParameters(self.miner.minerinfo.miner_type, 10000, 40, 55, 60*10, maxtempreset=None)
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)

        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertFalse(rules.has_reboot_rule())

    def test_brokenrule(self):
        rule = BrokenRule(self.miner, '', '')
        self.assertTrue(str(rule) == 'broke Test: ')

    def test_hasreading(self):
        self.assertFalse(MinerStatisticsRule.hasreading(None))
        self.assertTrue(MinerStatisticsRule.hasreading(1))
        self.assertFalse(MinerStatisticsRule.hasreading(0))
        self.assertFalse(MinerStatisticsRule.hasreading_num(None))

    def test_only_one_reset(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', ''))
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', ''))
        self.assertTrue(len(rules.brokenrules) == 1)

    def test_only_one_reboot(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', 'reboot'))
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', 'reboot'))
        self.assertTrue(len(rules.brokenrules) == 1)

    def test_reset_leaves_reboot(self):
        rules = MinerStatisticsRule(self.miner, None, None)
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', 'reboot'))
        rules.addbrokenrule(BrokenRule(self.miner, 'restart', ''))
        self.assertTrue(len(rules.brokenrules) == 1)
        self.assertTrue(rules.brokenrules[0].parameter == 'reboot')

    def test_hardware_errors_alert(self):
        '''test when hardware errors exceeced'''
        self.minerstats.hardware_errors = 100
        params = RuleParameters(self.miner.minerinfo.miner_type, 13500, 40, 55, 60*10, None, 99, '10s')
        rules = MinerStatisticsRule(self.miner, self.minerstats, params)
        isbroken = rules.isbroken()
        self.assertTrue(isbroken)
        self.assertTrue(len(rules.brokenrules) > 0)


if __name__ == '__main__':
    unittest.main()
