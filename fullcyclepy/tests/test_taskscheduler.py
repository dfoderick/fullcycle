import unittest
import datetime
from helpers.taskschedule import TaskSchedule

class TestTaskscheduler(unittest.TestCase):
    def test_task_scheduler_disabled(self):
        task = TaskSchedule()
        task.interval = 0
        self.assertFalse(task.is_time_to_run())

    def test_task_scheduler_runinit(self):
        task = TaskSchedule(run_on_init=True)
        task.interval = 0
        self.assertFalse(task.is_time_to_run())

    def test_task_scheduler_enabled(self):
        task = TaskSchedule(run_on_init=True)
        task.interval = 1
        self.assertTrue(task.is_time_to_run())

    def test_task_scheduler_enabled_1(self):
        task = TaskSchedule()
        task.interval = 1
        task.start = None
        task.lastrun = None
        self.assertTrue(task.is_time_to_run())

    def test_task_scheduler_enabled_2(self):
        task = TaskSchedule()
        task.start = datetime.datetime.now()
        task.interval = 1
        task.lastrun = None
        self.assertTrue(task.is_time_to_run())

    def test_task_scheduler_enabled_3(self):
        task = TaskSchedule()
        task.interval = 1
        task.start = datetime.datetime.now()
        task.lastrun = datetime.datetime.now() - datetime.timedelta(seconds=task.interval)
        self.assertTrue(task.is_time_to_run())

    def test_task_scheduler_not_run_yet(self):
        task = TaskSchedule()
        task.interval = 1
        task.start = datetime.datetime.now()
        task.lastrun = datetime.datetime.now()
        self.assertFalse(task.is_time_to_run())

if __name__ == '__main__':
    unittest.main()
