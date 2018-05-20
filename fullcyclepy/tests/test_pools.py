'''unit tests for pools'''
import unittest
from domain.mining import Pool, AvailablePool

class TestPools(unittest.TestCase):
    '''test'''
    def p_same_as_partial_match(self):
        '''test'''
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, namedpool.url, 'workername.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertTrue(is_same)

    def p_same_as_partial_match_case(self):
        '''test'''
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, \
            'tcp://STRATUM.POOL.COM', 'workername.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertTrue(is_same)

    def p_same_as_partial_not_match(self):
        '''test'''
        namedpool = Pool('S9', 'CoolPool', 'tcp://stratum.pool.com', 'workername.', 0)
        available_pool = AvailablePool('S9', None, namedpool.url, 'notyours.MinerName', 'x', 0)
        is_same = namedpool.is_same_as(available_pool)
        self.assertTrue(is_same)

if __name__ == '__main__':
    unittest.main()
