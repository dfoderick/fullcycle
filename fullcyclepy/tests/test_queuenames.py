import unittest
from helpers.queuehelper import QueueName

class TestQueuenames(unittest.TestCase):
    def test_queue_valid_name(self):
        self.assertTrue(QueueName.has_value(QueueName.Q_ALERT.value))

    def test_queue_invalid_name(self):
        self.assertFalse(QueueName.has_value('notaqueuename'))

    def test_queue_alert(self):
        self.assertTrue(str(QueueName.Q_ALERT) == 'q_alert')

    def test_queue_value(self):
        self.assertTrue(QueueName.value(QueueName.Q_ALERT) == 'alert')

if __name__ == '__main__':
    unittest.main()
