import os
import unittest
import backend.fcmutils as utils
#from backend.fcmapp import ApplicationService
from domain.mining import AvailablePool
from domain.rep import MinerRepository, PoolRepository, LoginRepository, RuleParametersRepository
from messaging.schema import AvailablePoolSchema

class TestApp(unittest.TestCase):
    def test_app_json_serialize(self):
        pool = AvailablePool('S9', None, 'url', 'user', 'x', 0)
        strpool = utils.jsonserialize(AvailablePoolSchema(), pool)
        self.assertTrue(isinstance(strpool, str))
        self.assertFalse(strpool.startswith('['))

    def test_rep_miner_repository(self):
        homedirectory = os.path.dirname(__file__)
        config = os.path.join(homedirectory, '../backend/config/miners.conf')
        rep = MinerRepository()
        miners = rep.readminers(config)
        self.assertTrue(miners)
        miner = rep.getminerbyname(miners[0].name, config)
        self.assertTrue(miner)

    def test_rep_pool_repository(self):
        homedirectory = os.path.dirname(__file__)
        config = os.path.join(homedirectory, '../backend/config/pools.conf')
        rep = PoolRepository()
        pools = rep.readpools(config)
        self.assertTrue(pools)
        #todo: rep.add

    def test_rep_login_repository(self):
        homedirectory = os.path.dirname(__file__)
        config = os.path.join(homedirectory, '../backend/config/ftp.conf')
        rep = LoginRepository()
        login = rep.readlogins(config)
        self.assertTrue(login)


    def test_rep_rules_repository(self):
        homedirectory = os.path.dirname(__file__)
        config = os.path.join(homedirectory, '../backend/config/rules.conf')
        rep = RuleParametersRepository()
        rules = rep.readrules(config)
        self.assertTrue(rules)

    #AppService needs cache to be mocked first

    #def test_app_knownpools(self):
    #    app = ApplicationService(component='test')
    #    app.startup()
    #    pools = app.pools.knownpools()
    #    self.assertTrue(len(pools) > 0)
    #    for pool in pools:
    #        self.assertTrue(isinstance(pool, AvailablePool))

    #def test_app_no_dupe_miners(self):
    #    app = ApplicationService(component='test')
    #    app.cache.purge()
    #    app.startup()
    #    original_miners = app.knownminers()
    #    miner = Miner("unittest", None, "", "unitip", "unitport", "", "")
    #    #add the test miner
    #    app.updateknownminer(miner)
    #    miners_withtest = app.knownminers()
    #    #put same in cache should not increase count
    #    app.updateknownminer(miner)
    #    miners_afterputtingtwice = app.knownminers()
    #    self.assertTrue(len(miners_withtest) == len(miners_afterputtingtwice))

    #def test_app_update_miner(self):
    #    app = ApplicationService(component='test')
    #    app.cache.purge()
    #    app.startup()
    #    original_miners = app.knownminers()
    #    miner = Miner("unittest", None, "", "unitip", "unitport", "", "")
    #    #add the test miner
    #    app.updateknownminer(miner)
    #    miners_withtest = app.knownminers()
    #    #put same in cache should not increase count
    #    #this simulates a miner getting queries and minerid has changed
    #    miner_updated = Miner("unittest", None, "", "unitip", "unitport", "", "")
    #    miner_updated.minerid="unittest_unique"
    #    app.updateknownminer(miner_updated)
    #    miners_afterputtingtwice = app.knownminers()
    #    self.assertTrue(len(miners_withtest) == len(miners_afterputtingtwice))
    #    miner_from_cache = app.getknownminer(miner_updated)
    #    self.assertIsNotNone(miner_from_cache)

if __name__ == '__main__':
    unittest.main()
