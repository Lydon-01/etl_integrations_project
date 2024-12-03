# utils/run_script.py
"""
Simple re-usable script runner to start direct path scripts
"""

import os
import sys
import subprocess
from colorama import Fore, Style

sys.path.append(os.getcwd())


def run_script(script_path):
    abs_file_path = os.path.abspath(script_path)

    print(f"{Fore.CYAN}Attempting to run: {abs_file_path}{Style.RESET_ALL}")

    if not os.path.exists(abs_file_path):
        print(f"{Fore.RED}The file {abs_file_path} was not found.{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Make sure you're running this script from the project root directory.{Style.RESET_ALL}"
        )
        return

    try:
        subprocess.run([sys.executable, abs_file_path], check=True)
        print(f"{Fore.GREEN}File executed successfully.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(
            f"{Fore.RED}An error occurred while running the file: {e}{Style.RESET_ALL}"
        )
