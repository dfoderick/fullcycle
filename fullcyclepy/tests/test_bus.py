import unittest
from helpers.queuehelper import QueueName
from backend.fcmapp import InfrastructureService
from backend.fcmbus import Bus

class Test_bus(unittest.TestCase):
    def make_bus(self):
        return Bus(InfrastructureService('', '', '', '', '', ''))

    def test_bus_get_name_q(self):
        bus = self.make_bus()
        self.assertTrue(bus.get_queue_name(QueueName.Q_ALERT) == "alert")

    def test_bus_get_name_str(self):
        bus = self.make_bus()
        self.assertTrue(bus.get_queue_name("alert") == "alert")

if __name__ == '__main__':
    unittest.main()
