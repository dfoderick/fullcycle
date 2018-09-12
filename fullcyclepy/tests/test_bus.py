import unittest
from helpers.queuehelper import QueueName
#from backend.fcmapp import InfrastructureService
from backend.fcmbus import Bus

class test_bus(unittest.TestCase):
    #@classmethod
    #def make_bus(self):
    #    return Bus(InfrastructureService('', '', '', '', '', ''))

    def test_bus_get_name_q(self):
        #bus = Test_bus.make_bus()
        self.assertTrue(Bus.get_queue_name(QueueName.Q_ALERT) == "alert")

    def test_bus_get_name_str(self):
        #bus = Test_bus.make_bus()
        self.assertTrue(Bus.get_queue_name("alert") == "alert")

if __name__ == '__main__':
    unittest.main()
