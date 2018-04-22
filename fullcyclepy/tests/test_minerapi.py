'''test miner api'''
import unittest
from helpers.antminerhelper import MinerMonitorException

class TestException(unittest.TestCase):
    def test_exception_is_timed_out(self):
        '''test'''
        ex = MinerMonitorException('monitor timed out')
        self.assertTrue(ex.istimedout())

    def test_exception_is_not_timed_out(self):
        '''test'''
        ex = MinerMonitorException('this is not the error you are looking for')
        self.assertFalse(ex.istimedout())

if __name__ == '__main__':
    unittest.main()
