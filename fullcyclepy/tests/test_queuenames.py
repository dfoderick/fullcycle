import unittest
from helpers.queuehelper import QueueName, QueueType, QueueEntry, QueueEntries

class TestQueuenames(unittest.TestCase):
    def test_queue_valid_name(self):
        self.assertTrue(QueueName.has_value(QueueName.Q_ALERT.value))

    def test_queue_invalid_name(self):
        self.assertFalse(QueueName.has_value('notaqueuename'))

    def test_queue_alert(self):
        self.assertTrue(str(QueueName.Q_ALERT) == 'q_alert')

    def test_queue_value(self):
        self.assertTrue(QueueName.value(QueueName.Q_ALERT) == 'alert')

    def test_queue_type(self):
        self.assertTrue(QueueType.broadcast == 'broadcast')
        self.assertTrue(QueueType.publish == 'publish')

    def test_queue_entry(self):
        q = QueueEntry('','','')
        self.assertTrue(q)

    def test_queue_entries(self):
        q = QueueEntries()
        self.assertTrue(q)
        q.add('test','test')
        q.addbroadcast('qbroad','test')
        q.addalert('msg')
        self.assertTrue(q.hasentries())

if __name__ == '__main__':
    unittest.main()
