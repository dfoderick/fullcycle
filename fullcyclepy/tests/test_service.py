import unittest
import backend.fcmservice as service
import backend.fcmcache as cache
import domain.mining as mining

class TestService(unittest.TestCase):
    def getconfig(self):
        config = service.Configuration({'true.enabled':'true', 'false.enabled':'false'})
        return config

    def getcache(self):
        csh = cache.Cache(service.InfrastructureService('', '', '', 80, '', ''))
        return csh

    def test_pool_service(self):
        svc = service.PoolService(None, None)
        miner = mining.Miner('test')
        dto = svc.serialize(miner)
        self.assertTrue(dto)
        pool = mining.Pool('', '', '', '', 1)
        dto = svc.serialize(pool)
        self.assertTrue(dto)
        self.assertFalse(svc.serialize('x'))

    def test_pool_service_get(self):
        svc = service.PoolService(None, None)
        self.assertTrue(svc.get_all_pools())

    def test_pool_service_findpool(self):
        svc = service.PoolService(None, None)
        self.assertFalse(svc.findpool(mining.MinerCurrentPool(None)))

    def test_pool_1(self):
        svc = service.PoolService(None, None)
        env = svc.createmessageenvelope()
        self.assertTrue(env)

    def test_pool_2(self):
        svc = service.PoolService(self.getconfig(), self.getcache())
        env = svc.createmessageenvelope()
        self.assertTrue(svc.serializemessageenvelope(env))

    def test_pool_3(self):
        svc = service.PoolService(self.getconfig(), self.getcache())
        env = svc.createmessageenvelope()
        self.assertTrue(svc.deserializemessageenvelope(svc.serializemessageenvelope(env)))

    #def test_pool_knownpools(self):
    #redis not mocked yet
    #    svc = service.PoolService(self.getconfig(), self.getcache())
    #    self.assertFalse(svc.knownpools())

    def test_pool_getpool(self):
        svc = service.PoolService(self.getconfig(), self.getcache())
        miner = mining.Miner('test')
        self.assertFalse(svc.getpool(miner))

    def test_configuration(self):
        config = service.Configuration({'a':'b'})
        self.assertTrue(config.get('a'))
        self.assertFalse(config.get('x'))

    def test_configuration_isenabled(self):
        config = service.Configuration({'true.enabled':'true', 'false.enabled':'false'})
        self.assertTrue(config.is_enabled('true'))
        self.assertFalse(config.is_enabled('false'))
        self.assertFalse(config.is_enabled('x'))

    def test_telegram(self):
        config = service.Configuration({'true.enabled':'true', 'false.enabled':'false'})
        tele = service.Telegram(config, None)
        self.assertTrue(tele)
        tele.sendmessage('x')
        tele.sendphoto('x')

if __name__ == '__main__':
    unittest.main()
