import os
import sys
import subprocess
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Use os.path.join for path handling
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class CodeFormatter:
    def __init__(self, directory):
        self.directory = directory

    def format(self):
        formatted_count = 0
        error_count = 0

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".py"):
                    success = self._format_file(os.path.join(root, file))
                    if success:
                        formatted_count += 1
                    else:
                        error_count += 1

        print(f"\n{Fore.GREEN}Formatted {formatted_count} files successfully.")
        if error_count > 0:
            print(f"{Fore.RED}Encountered errors in {error_count} files.")

    def _format_file(self, file_path):
        try:
            # Use Black to format the file
            command = [sys.executable, "-m", "black", file_path]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"{Fore.CYAN}Formatted: {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error formatting {file_path}: {e}")
            print(f"{Fore.YELLOW}Error output: {e.stderr}")
            return False


if __name__ == "__main__":
    formatter = CodeFormatter(".")
    formatter.format()
