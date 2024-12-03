from config import config as cfg
import sys
import signal
import os
import subprocess
import time
import schedule
from colorama import Fore, Style, init
import logging
import json
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class c_task_scheduler:
    def __init__(self):
        self.FREQUENCY_MAP = {
            "quarterhourly": schedule.every(15).minutes.do,
            "hourly": schedule.every().hour.do,
            "daily": schedule.every().day.at("00:00").do,
            "weekly": schedule.every().week.do,
        }
        self.start_delay = cfg.SCHEDULE_CONFIG.get("start_delay_seconds", 5)
        self.log_messages = []

    def is_job_scheduled(self, task_name):
        for job in schedule.jobs:
            if job.job_func.__name__ == f"run_task_{task_name}":
                return True
        return False

    def list_scheduled_jobs_and_tasks(self):
        print(Fore.CYAN + "Scheduled Jobs and Tasks:")
        scheduled_tasks = []
        for task_name, config in cfg.SCHEDULE_CONFIG["jobs"].items():
            frequency = config.get("frequency", "hourly")
            is_scheduled = self.is_job_scheduled(task_name)
            status = "Scheduled" if is_scheduled else "Not scheduled"

            task_info = {
                "task_name": task_name,
                "frequency": frequency,
                "status": status,
            }
            scheduled_tasks.append(task_info)
            self.log_messages.append(json.dumps(task_info))

            print(f"- {task_name}: {frequency} ({status})")

        return scheduled_tasks

    def is_task_running(self, task_name):
        try:
            result = subprocess.check_output(
                f"ps aux | grep '[p]ython3 {task_name}( |$)'", shell=True
            ).decode("utf-8")
            return bool(result.strip())
        except subprocess.CalledProcessError:
            return False

    def run_task(self, task_path):
        task_name = os.path.basename(task_path)
        if self.is_task_running(task_name):
            print(f"Task {task_name} is already running. Skipping...")
            self.log_messages.append(
                json.dumps(
                    {
                        "action": "skip_task",
                        "task_name": task_name,
                        "reason": "already_running",
                    }
                )
            )
            return
        try:
            print(f"Starting task: {task_path}...")
            subprocess.Popen(["python3", task_path])
            self.log_messages.append(
                json.dumps(
                    {
                        "action": "start_task",
                        "task_name": task_name,
                        "status": "success",
                    }
                )
            )
        except Exception as e:
            print(f"Failed to start task {task_path}. Error: {e}")
            self.log_messages.append(
                json.dumps(
                    {
                        "action": "start_task",
                        "task_name": task_name,
                        "status": "failed",
                        "error": str(e),
                    }
                )
            )

    def start_all_tasks(self):
        for task_name, config in cfg.SCHEDULE_CONFIG["jobs"].items():
            path = config.get("path")
            if not self.is_task_running(os.path.basename(path)):
                self.run_task(path)
                time.sleep(self.start_delay)
            else:
                print(f"Task {task_name} is already running. Skipping...")

    def create_task_runner(self, task_name, path):
        def task_runner():
            self.run_task(path)

        task_runner.__name__ = f"run_task_{task_name}"
        return task_runner

    def start_scheduler(self):
        if self.is_task_running("start_scheduler.py"):
            print("Scheduler is already running. Exiting...")
            self.log_messages.append(
                json.dumps({"action": "start_scheduler", "status": "already_running"})
            )
            sys.exit(0)

        self.start_all_tasks()

        for task_name, config in cfg.SCHEDULE_CONFIG["jobs"].items():
            path = config.get("path")
            frequency = config.get("frequency", "hourly")
            if frequency in self.FREQUENCY_MAP and not self.is_job_scheduled(task_name):
                task_runner = self.create_task_runner(task_name, path)
                self.FREQUENCY_MAP[frequency](task_runner)
                self.log_messages.append(
                    json.dumps(
                        {
                            "action": "schedule_task",
                            "task_name": task_name,
                            "frequency": frequency,
                        }
                    )
                )

        self.create_log_file()

        print("Running due tasks...")
        schedule.run_all()

        print("Scheduler has finished setting up tasks.")
        self.log_messages.append(
            json.dumps({"action": "scheduler_finished", "status": "success"})
        )
        self.create_log_file()

    @staticmethod
    def terminate_process(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(10):  # Wait up to 1 second
                time.sleep(0.1)
                os.kill(pid, 0)  # This will raise an OSError if the process is gone
            # If we get here, the process didn't terminate, so we'll try SIGKILL
            os.kill(pid, signal.SIGKILL)
        except OSError:
            # Process has already terminated
            pass

    def stop_scheduler(self):
        self.log_messages.append(
            json.dumps({"action": "stop_scheduler", "status": "starting"})
        )

        tasks_stopped = 0
        tasks_failed = 0
        current_pid = os.getpid()
        start_time = time.time()
        timeout = 60  # 60 seconds timeout

        for task_name, config in cfg.SCHEDULE_CONFIG["jobs"].items():
            task_path = config.get("path")
            task_name = os.path.basename(task_path)
            try:
                pids = (
                    subprocess.check_output(
                        f"pgrep -f '{task_name}' | grep -v {current_pid}", shell=True
                    )
                    .decode()
                    .strip()
                    .split("\n")
                )
                print(f"Found PIDs for task {task_name}: {pids}")  # Debugging output
                for pid in pids:
                    if pid:
                        try:
                            self.terminate_process(int(pid))
                            self.log_messages.append(
                                json.dumps(
                                    {
                                        "action": "stop_task",
                                        "task_name": task_name,
                                        "pid": pid,
                                        "status": "success",
                                    }
                                )
                            )
                            tasks_stopped += 1
                        except ProcessLookupError:
                            self.log_messages.append(
                                json.dumps(
                                    {
                                        "action": "stop_task",
                                        "task_name": task_name,
                                        "pid": pid,
                                        "status": "failed",
                                        "reason": "process_not_found",
                                    }
                                )
                            )
                        except PermissionError:
                            self.log_messages.append(
                                json.dumps(
                                    {
                                        "action": "stop_task",
                                        "task_name": task_name,
                                        "pid": pid,
                                        "status": "failed",
                                        "reason": "permission_denied",
                                    }
                                )
                            )
                        time.sleep(0.5)  # Half-second delay after stopping each task
            except subprocess.CalledProcessError:
                self.log_messages.append(
                    json.dumps(
                        {
                            "action": "stop_task",
                            "task_name": task_name,
                            "status": "failed",
                            "reason": "not_running",
                        }
                    )
                )
                tasks_failed += 1

        # Check if all tasks have stopped within the timeout period
        while time.time() - start_time < timeout:
            if not any(
                self.is_task_running(task["task_name"])
                for task in self.list_scheduled_jobs_and_tasks()
            ):
                print("All tasks have been stopped successfully.")
                break
            time.sleep(1)
        else:
            print("Warning: Not all tasks could be stopped within the timeout period.")

        if tasks_stopped > 0:
            print(f"Scheduler has successfully stopped {tasks_stopped} task(s).")
        else:
            print("No tasks were running or could be stopped.")

        if tasks_failed > 0:
            print(
                f"Failed to stop {tasks_failed} task(s). They may not have been running."
            )

        self.log_messages.append(
            json.dumps(
                {
                    "action": "stop_scheduler",
                    "status": "finished",
                    "tasks_stopped": tasks_stopped,
                    "tasks_failed": tasks_failed,
                }
            )
        )

        self.create_log_file()

        print("Scheduler has finished stopping tasks.")

    def create_log_file(self):
        # Generate date and time components
        log_date = datetime.now().strftime("%Y%m%d")  # YYYYMMDD
        log_time = datetime.now().strftime("%H%M%S")  # HHMMSS

        # Define the log directory structure
        log_dir = os.path.join(cfg.LOG_DIR, "scheduler", log_date)

        # Ensure the directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Define the log file name
        log_file_name = f"{log_time}.json"
        log_file_path = os.path.join(log_dir, log_file_name)

        # Collect data for logging
        scheduled_tasks = self.list_scheduled_jobs_and_tasks()
        running_tasks = [
            task for task in scheduled_tasks if self.is_task_running(task["task_name"])
        ]

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "scheduler_status": "running",
            "scheduled_tasks": scheduled_tasks,
            "running_tasks": running_tasks,
            "config": {
                "start_delay": self.start_delay,
                "jobs": cfg.SCHEDULE_CONFIG["jobs"],
            },
            "log_messages": self.log_messages,
        }

        # Write the log data to the JSON file
        with open(log_file_path, "w") as log_file:
            json.dump(log_data, log_file, indent=2)

        # Clear log messages after writing to file
        self.log_messages = []

        # Print the log file creation message
        print(Fore.CYAN + f"Scheduler log created: {log_file_path}")
        return log_file_path


if __name__ == "__main__":
    scheduler = c_task_scheduler()

    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        scheduler.stop_scheduler()
    else:
        scheduler.start_scheduler()
