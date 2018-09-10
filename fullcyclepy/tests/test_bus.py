import unittest
from helpers.queuehelper import QueueName
from backend.fcmapp import Bus, InfrastructureService

class Test_bus(unittest.TestCase):
    def test_bus_get_name_q(self):
        bus = Bus(InfrastructureService('','','','','',''))
        self.assertTrue(bus.get_queue_name(QueueName.Q_ALERT) == "alert")

    def test_bus_get_name_str(self):
        bus = Bus(InfrastructureService('','','','','',''))
        self.assertTrue(bus.get_queue_name("alert") == "alert")

if __name__ == '__main__':
    unittest.main()
