import unittest
from backend.fcmapp import ApplicationService
from domain.mining import AvailablePool
from messaging.schema import AvailablePoolSchema

class Test_test_app(unittest.TestCase):
    def test_app_json_serialize(self):
        app = ApplicationService(component='test')
        pool = AvailablePool('S9', None, 'url', 'user', 'x', 0)
        strpool = app.jsonserialize(AvailablePoolSchema(), pool)
        self.assertTrue(isinstance(strpool, str))
        self.assertFalse(strpool.startswith('['))

    def test_app_knownpools(self):
        app = ApplicationService(component='test')
        pools = app.knownpools()
        for pool in pools:
            self.assertTrue(isinstance(pool,AvailablePool))

if __name__ == '__main__':
    unittest.main()
