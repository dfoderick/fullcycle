import unittest
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

if __name__ == '__main__':
    unittest.main()
