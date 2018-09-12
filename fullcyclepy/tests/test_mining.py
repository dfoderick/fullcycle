'''test mining domain'''
import unittest
import datetime
import domain.minerstatistics
from domain.mining import Miner, MinerStatus, MinerInfo, MinerApiCall

class TestMiner(unittest.TestCase):
    def test_miner_is_not_disabled(self):
        miner = Miner("test", '', '', '', '', '', '', '', '')
        self.assertFalse(miner.is_disabled())

    def test_miner_is_disabled(self):
        miner = Miner("#test", '', '', '', '', '', '', '', '')
        self.assertTrue(miner.is_disabled())

    def test_miner_key_is_id(self):
        miner = Miner("test", minerid='unittest')
        self.assertTrue(miner.key() == 'unittest')

    def test_miner_key_not_unknown(self):
        miner = Miner('test', minerid='unknown', ipaddress='unittest', port='1234')
        self.assertTrue(miner.key() == 'unittest:1234')

    def test_miner_key_is_networkid(self):
        miner = Miner("test", networkid={'unittest1', 'unittest2'})
        self.assertTrue(miner.key() == str({'unittest1', 'unittest2'}))

    def test_key_notempty_net(self):
        miner = Miner("test", networkid={})
        self.assertFalse(miner.key() == str({}))

    def test_miner_key_is_ip(self):
        miner = Miner("test", ipaddress='unittest', port='1234')
        self.assertTrue(miner.key() == 'unittest:1234')

    def test_miner_key_is_name(self):
        miner = Miner("test")
        self.assertTrue(miner.key() == 'test')

    def test_miner_formattime_now(self):
        miner = Miner('test')
        miner.lastmonitor = datetime.datetime.utcnow()
        self.assertTrue(miner.formattime(miner.lastmonitor))

    def test_miner_formattime_string(self):
        miner = Miner('test')
        miner.lastmonitor = '2018-04-11T01:28:45+00:00'
        self.assertTrue(miner.formattime(miner.lastmonitor))

    def test_miner_uses_custom(self):
        miner = Miner('test')
        miner.ftpport = '99'
        miner.set_ftp_port('22')
        self.assertTrue(miner.ftpport == '99')

    def test_miner_uses_default(self):
        miner = Miner('test')
        miner.ftpport = ''
        miner.set_ftp_port('22')
        self.assertTrue(miner.ftpport == '22')

    def test_miner_status_set_last_update(self):
        miner = Miner('test')
        self.assertTrue(not miner.laststatuschanged)
        miner.status = MinerStatus.Offline
        self.assertTrue(miner.laststatuschanged)

    def test_miner_status_change_keeps_original(self):
        miner = Miner('test')
        miner.status = MinerStatus.Offline
        self.assertTrue(miner.laststatuschanged)
        originalstatuschangetime = miner.laststatuschanged
        miner.status = MinerStatus.Offline
        self.assertTrue(miner.laststatuschanged == originalstatuschangetime)

    def test_miner_status_no_you_cant(self):
        miner = Miner('test')
        def set_status_test():
            miner.status = 'you can be anyting'
        self.assertRaises(ValueError, set_status_test)

    def test_miner_reset_offline_count(self):
        miner = Miner('test')
        self.assertTrue(miner.offlinecount == 0)
        self.assertTrue(miner.is_send_offline_alert())
        miner.offline_now()
        miner.offline_now()
        miner.offline_now()
        miner.offline_now()
        self.assertFalse(miner.is_send_offline_alert())
        miner.online_now()
        self.assertTrue(miner.offlinecount == 0)
        self.assertTrue(miner.is_send_offline_alert())

    def test_miner_setminerinfo(self):
        miner = Miner('test')
        minerinfo = MinerInfo('testminertype', miner.minerid)
        miner.setminerinfo(minerinfo)
        self.assertTrue(miner.miner_type == minerinfo.miner_type)

    def test_miner_shouldmonitor(self):
        miner = Miner('test')
        miner.lastmonitor = ""
        self.assertTrue(miner.should_monitor())

    def test_miner_elapsed_format(self):
        miner = Miner('test')
        miner.minerstats = domain.minerstatistics.MinerStatistics(miner)
        self.assertTrue(miner.minerstats.format_elapsed() == "0:0:0:0")

    def test_miner_monitored_nothing_none(self):
        miner = Miner('test')
        miner.monitored(None, None, None, None)
        self.assertTrue(miner.lastmonitor is None)

    def test_miner_monitored_not_nothing_ismonitored(self):
        miner = Miner('test')
        stats = domain.minerstatistics.MinerStatistics(miner)
        miner.monitored(stats, pool=None, info=None, sec=None)
        self.assertFalse(miner.lastmonitor is None)

    def test_miner_monitored_timer(self):
        miner = Miner('test')
        stats = domain.minerstatistics.MinerStatistics(miner)
        apicall = MinerApiCall(miner)
        apicall.start()
        apicall.stop()
        miner.monitored(stats, pool=None, info=None, sec=apicall.elapsed())
        self.assertFalse(miner.lastmonitor is None)

    def test_miner_update(self):
        miner = Miner('test')
        miner.ipaddress = 'ip1'
        minerupdate = Miner('test')
        minerupdate.ipaddress = 'ip2'
        miner.updatefrom(minerupdate)
        self.assertTrue(miner.ipaddress == minerupdate.ipaddress)

    def test_miner_no_update(self):
        miner = Miner('test')
        miner.ipaddress = 'ip1'
        minerupdate = Miner('test')
        minerupdate.ipaddress = None
        miner.updatefrom(minerupdate)
        self.assertTrue(miner.ipaddress != minerupdate.ipaddress)

    def test_miner_update_port(self):
        miner = Miner('test')
        miner.port = 'port1'
        minerupdate = Miner('test')
        minerupdate.port = 'port2'
        miner.updatefrom(minerupdate)
        self.assertTrue(miner.port == minerupdate.port)

if __name__ == '__main__':
    unittest.main()
