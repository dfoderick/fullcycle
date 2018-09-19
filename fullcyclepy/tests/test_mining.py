'''test mining domain'''
import unittest
import datetime
import domain.minerstatistics
from domain.mining import Miner, MinerStatus, MinerInfo, MinerApiCall, MinerCommand, MinerCurrentPool

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

    def test_miner_formattime_with_fraction(self):
        miner = Miner('test')
        miner.lastmonitor = '2018-04-11T01:28:45.3821739+00:00'
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

    def test_miner_stats_summary(self):
        miner = Miner('test')
        miner.minerstats = domain.minerstatistics.MinerStatistics(miner)
        summary = miner.minerstats.stats_summary()
        self.assertTrue(summary == '0 0/0 0:0:0:0')

    def test_miner_monitored_nothing_none(self):
        miner = Miner('test')
        miner.monitored(None, None, None, None)
        self.assertTrue(miner.lastmonitor is None)

    def test_miner_monitored_not_nothing_ismonitored(self):
        miner = Miner('test')
        stats = domain.minerstatistics.MinerStatistics(miner)
        miner.monitored(stats, pool=None, info=None, sec=None)
        self.assertFalse(miner.lastmonitor is None)

    def test_miner_monitored_pool(self):
        miner = Miner('test')
        stats = domain.minerstatistics.MinerStatistics(miner)
        miner.monitored(stats, pool=MinerCurrentPool(miner), info=None, sec=None)
        self.assertTrue(miner.minerpool)

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
        miner.minerid='test'
        miner.ipaddress = 'ip1'
        miner.location = 'location1'
        miner.in_service_date = datetime.datetime.now().replace(second=0, microsecond=0)
        minerupdate = Miner('test1')
        minerupdate.minerid='test1'
        minerupdate.ipaddress = 'ip2'
        minerupdate.location = 'location2'
        minerupdate.in_service_date = datetime.datetime.now()
        miner.updatefrom(minerupdate)
        self.assertFalse(miner.ipaddress == minerupdate.ipaddress)
        minerupdate.minerid = miner.minerid
        miner.updatefrom(minerupdate)
        self.assertTrue(miner.ipaddress == minerupdate.ipaddress)
        self.assertTrue(miner.location == minerupdate.location)
        self.assertTrue(miner.in_service_date == minerupdate.in_service_date)

    def test_miner_is_unknown(self):
        miner = Miner('test')
        miner.minerid = "unknown"
        self.assertTrue(miner.is_unknown)

    def test_miner_is_known(self):
        miner = Miner('test')
        miner.minerid = "123.123.123.123"
        self.assertFalse(miner.is_unknown)

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

    def test_miner_create(self):
        values = []
        values.append({"name":"UnitTest"})
        values.append({"minerid": "1"})
        values.append({"ipaddress": "123.123.123.123"})
        values.append({"port": "987"})
        values.append({"location": "rack"})
        values.append({"in_service_date": "2018-01-01T08:00:00.000Z"})
        miner = Miner.create(values)
        self.assertTrue(miner.name == "UnitTest")
        self.assertTrue(miner.minerid == "1")
        self.assertTrue(miner.ipaddress == "123.123.123.123")
        self.assertTrue(miner.port == "987")
        self.assertTrue(miner.location == "rack")
        self.assertTrue(miner.in_service_date.date() == datetime.date(2018,1, 1) )

    def test_miner_key_original(self):
        miner = Miner('test')
        miner.minerid = "unittest"
        self.assertTrue(miner.is_key_updated)

    def test_miner_command(self):
        command = MinerCommand()
        self.assertTrue(command.command == '')
        self.assertTrue(command.parameter == '')

    def test_miner_currentpoolname(self):
        miner = Miner('test')
        self.assertTrue(miner.currentpoolname() == '?')
        miner.minerpool = MinerCurrentPool(miner, 'test pool', 'test worker', allpools={}, poolname = 'unit test')
        self.assertTrue(miner.currentpoolname() == 'unit test')
        self.assertFalse(miner.minerpool.findpoolnumberforpool('test pool', 'test worker'))

    def test_miner_pools_available(self):
        miner = Miner('test')
        self.assertTrue(miner.pools_available is None)
        miner.minerpool = MinerCurrentPool(miner, 'test pool', 'test worker', allpools={})
        self.assertTrue(len(miner.pools_available) == 0)
        miner.minerpool.allpools = {
      "POOLS": [
        {
          "Pool Stale%": 0,
          "Accepted": 421743,
          "Difficulty Stale": 0,
          "Stratum URL": "test",
          "Rejected": 85,
          "Difficulty Accepted": 6587318272,
          "Best Share": 4019408192,
          "User": "test",
          "Stratum Active": True,
          "Difficulty Rejected": 1343488,
          "Diff": "16.4K",
          "Remote Failures": 3,
          "Discarded": 1094132,
          "Long Poll": "N",
          "Proxy": "",
          "Priority": 0,
          "Has GBT": False,
          "Pool Rejected%": 0.0204,
          "Stale": 63,
          "Last Share Difficulty": 16384,
          "Diff1 Shares": 0,
          "Has Stratum": True,
          "Status": "Alive",
          "URL": "test",
          "Quota": 1,
          "Last Share Time": "0:00:05",
          "Getworks": 70163,
          "Get Failures": 3,
          "POOL": 3,
          "Proxy Type": ""
        }]}
        self.assertTrue(len(miner.pools_available) > 0)
        self.assertTrue(miner.minerpool.findpoolnumberforpool('test', 'test'))
        self.assertFalse(miner.minerpool.findpoolnumberforpool('not', 'found'))

    def test_miner_summary(self):
        miner = Miner("test", '', '', '', '', '', '', '', '')
        self.assertTrue(miner.summary() is not None)
        miner.status = MinerStatus.Online
        self.assertTrue(miner.summary() is not None)
        miner.minerstats = None
        self.assertTrue(miner.summary() is not None)
        miner.minerstats = domain.minerstatistics.MinerStatistics(miner)
        self.assertTrue(miner.summary() is not None)
 
    def test_miner_todate(self):
        dt = Miner.to_date(datetime.datetime.now())
        self.assertTrue(isinstance(dt, datetime.datetime))

    def test_miner_uptime(self):
        miner = Miner("test", '', '', '', '', '', '', '', '')
        self.assertTrue(miner.uptime(1))

    def test_miner_monitorresponsetime(self):
        miner = Miner("test", '', '', '', '', '', '', '', '')
        self.assertTrue(miner.monitorresponsetime() == 0)
        miner.monitored(domain.minerstatistics.MinerStatistics(miner), None, None, 1)
        self.assertTrue(miner.monitorresponsetime() > 0)

    def test_miner_can_monitor(self):
        miner = Miner("test", '', '', '', '', '', '', '', '')
        self.assertFalse(miner.can_monitor())
        miner.ipaddress = '123.123.123.123'
        self.assertFalse(miner.can_monitor())
        miner.port = '4028'
        self.assertTrue(miner.can_monitor())

    def test_miner_should_monitor(self):
        miner = Miner("#test", '', '', '', '', '', '', '', '')
        self.assertTrue(miner.should_monitor())
        miner.monitored(domain.minerstatistics.MinerStatistics(miner), None, None, None)
        self.assertFalse(miner.should_monitor())
        miner.name="test"
        self.assertTrue(miner.should_monitor())
        miner.status = MinerStatus.Disabled
        self.assertTrue(miner.should_monitor())

if __name__ == '__main__':
    unittest.main()
