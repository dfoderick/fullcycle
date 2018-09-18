'''unit tests for pools'''
import unittest
from domain.mining import Pool, AvailablePool
from domain.minerpool import MinerPool

class TestPools(unittest.TestCase):
    def test_availablepool_key(self):
        available_pool = AvailablePool('S9', None, 'url', 'user', 'x', 0)
        self.assertTrue(available_pool.key == 'url|user')

    def test_same_as_partial_match(self):
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, namedpool.url, 'workername.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertTrue(is_same)

    def test_same_as_partial_match_case(self):
        '''test'''
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, \
            namedpool.url.upper(), 'workername.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertTrue(is_same)

    def test_same_as_partial_not_match(self):
        '''test'''
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, namedpool.url, 'notyours.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertFalse(is_same)

    def test_pool_create(self):
        values = []
        values.append({"name":"UnitTest"})
        values.append({"pool_type": "unitpool"})
        values.append({"url": "unittest.com"})
        values.append({"user": "test"})
        values.append({"priority": "priority"})
        values.append({"password": "secret"})
        pool = Pool.create(values)
        self.assertTrue(pool.name == "UnitTest")
        self.assertTrue(pool.pool_type == "unitpool")
        self.assertTrue(pool.url == "unittest.com")
        self.assertTrue(pool.user == "test")
        self.assertTrue(pool.priority == "priority")
        self.assertTrue(pool.password == "secret")

    def test_minerpool(self):
        pool = MinerPool(None, 1, None)
        self.assertTrue(pool.priority == 1)

if __name__ == '__main__':
    unittest.main()
