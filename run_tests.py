from utils.format_code import CodeFormatter
import os
import sys
import unittest
import json
from datetime import datetime

# Ensure the current working directory is in the path
sys.path.append(os.getcwd())
from config import config as cfg  # noqa: E402

# Get the current date and time for the log file path (e.g., '20241129/1500.py')
current_datetime = datetime.now()
log_subdir = current_datetime.strftime("%Y%m%d")
log_filename = current_datetime.strftime("%H%M.json")
log_path = os.path.join(cfg.LOG_DIR, "tests", log_subdir)

# Ensure the log directory exists
os.makedirs(log_path, exist_ok=True)

log_file_path = os.path.join(log_path, log_filename)

if __name__ == "__main__":
    # Step 1: Format the code
    # CodeFormatter(".") --> best run manually

    # Step 2: Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    print(f"Discovered test cases: {suite}")

    # Run tests and log the results
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Prepare the log dictionary
    log_data = {
        "timestamp": current_datetime.isoformat(),
        "testsRun": result.testsRun,
        "wasSuccessful": result.wasSuccessful(),
        "failures": [],
        "errors": [],
    }

    # Add failures and errors to the log
    for failed_test, err in result.failures:
        log_data["failures"].append({"test": failed_test.id(), "error": err})

    for errored_test, err in result.errors:
        log_data["errors"].append({"test": errored_test.id(), "error": err})

    # Save the log as a JSON file
    with open(log_file_path, "w") as log_file:
        json.dump(log_data, log_file, indent=4)

    print(f"Test results saved to {log_file_path}")
