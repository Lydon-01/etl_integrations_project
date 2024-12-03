# scripts/start_load.py

import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.run_script import run_script

if __name__ == "__main__":
    script_path = "src/etl_integrations_project_lydon/extract/c_extract_data.py"
    run_script(script_path)
