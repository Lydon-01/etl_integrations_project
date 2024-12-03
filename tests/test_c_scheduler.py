import unittest
from unittest.mock import patch, MagicMock
from src.etl_integrations_project_lydon.scheduler.c_scheduler import (
    c_task_scheduler,
)
from config import config as cfg


class TestCScheduler(unittest.TestCase):

    @patch("schedule.jobs")
    def test_list_scheduled_jobs_and_tasks(self, mock_jobs):
        # Create a mock schedule job
        mock_job = MagicMock()
        mock_job.job_func.__name__ = "run_task_test_task"
        mock_jobs.__iter__.return_value = [mock_job]

        # Mock the config
        cfg.SCHEDULE_CONFIG = {
            "jobs": {
                "test_task": {"frequency": "hourly"},
                "another_task": {"frequency": "daily"},
            }
        }

        scheduler = c_task_scheduler()

        # Capture print output
        with patch("builtins.print") as mock_print:
            scheduled_tasks = scheduler.list_scheduled_jobs_and_tasks()

        # Assert the returned scheduled tasks
        self.assertEqual(len(scheduled_tasks), 2)
        self.assertEqual(scheduled_tasks[0]["task_name"], "test_task")
        self.assertEqual(scheduled_tasks[0]["frequency"], "hourly")
        self.assertEqual(scheduled_tasks[0]["status"], "Scheduled")
        self.assertEqual(scheduled_tasks[1]["task_name"], "another_task")
        self.assertEqual(scheduled_tasks[1]["frequency"], "daily")
        self.assertEqual(scheduled_tasks[1]["status"], "Not scheduled")

        # Assert that print was called with the correct messages
        mock_print.assert_any_call("\x1b[36mScheduled Jobs and Tasks:")
        mock_print.assert_any_call("- test_task: hourly (Scheduled)")
        mock_print.assert_any_call("- another_task: daily (Not scheduled)")

        # Print actual running tasks
        self.print_actual_running_tasks(scheduler)

    def print_actual_running_tasks(self, scheduler):
        print("\nActual Running Tasks:")
        for task_name, config in cfg.SCHEDULE_CONFIG["jobs"].items():
            if scheduler.is_task_running(task_name):
                print(f"- {task_name} is running")
            else:
                print(f"- {task_name} is not running")

    # In future test all functions in the scheduler class


if __name__ == "__main__":
    unittest.main()
