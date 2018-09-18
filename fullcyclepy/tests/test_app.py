import unittest
import backend.fcmutils as utils
#from backend.fcmapp import ApplicationService
from domain.mining import AvailablePool
from messaging.schema import AvailablePoolSchema

class TestApp(unittest.TestCase):
    def test_app_json_serialize(self):
        pool = AvailablePool('S9', None, 'url', 'user', 'x', 0)
        strpool = utils.jsonserialize(AvailablePoolSchema(), pool)
        self.assertTrue(isinstance(strpool, str))
        self.assertFalse(strpool.startswith('['))

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
