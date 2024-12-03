# Import the c_task_scheduler class
from src.etl_integrations_project_lydon.scheduler.c_scheduler import (
    c_task_scheduler,
)

if __name__ == "__main__":
    # Create an instance of the scheduler
    scheduler = c_task_scheduler()

    # Call the start_scheduler method
    scheduler.start_scheduler()
