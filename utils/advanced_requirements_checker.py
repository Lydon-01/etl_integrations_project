# advanced_requirements_checker.py

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

def get_python_versions() -> List[str]:
    """Get all installed Python versions."""
    versions = []
    for version in range(2, 12):  # Checking Python 2.x to 11.x
        for minor in range(20):  # Checking minor versions up to .19
            version_str = f"{version}.{minor}"
            try:
                subprocess.check_output(["python" + version_str, "--version"])
                versions.append(version_str)
            except subprocess.CalledProcessError:
                pass
            except FileNotFoundError:
                pass
    return versions

def get_virtual_env_paths() -> List[str]:
    """Get potential virtual environment paths."""
    venv_paths = []
    home = Path.home()
    
    # Common venv locations
    potential_paths = [
        home / ".virtualenvs",
        home / "venv",
        home / "virtualenv",
        Path("/opt/venv"),
        Path("/usr/local/venv"),
    ]
    
    for path in potential_paths:
        if path.is_dir():
            venv_paths.extend([str(p) for p in path.iterdir() if p.is_dir()])
    
    # Check for active virtual environment
    if "VIRTUAL_ENV" in os.environ:
        venv_paths.append(os.environ["VIRTUAL_ENV"])
    
    return venv_paths

def read_requirements(file_path: str) -> List[str]:
    """Read requirements from file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

def check_package(package: str, python_path: str) -> Tuple[bool, str]:
    """Check if a package is installed for a given Python path."""
    try:
        output = subprocess.check_output([python_path, "-m", "pip", "show", package], stderr=subprocess.DEVNULL)
        version = next((line.split(': ')[1] for line in output.decode().split('\n') if line.startswith('Version: ')), "Unknown")
        return True, version
    except subprocess.CalledProcessError:
        return False, ""

def check_packages(requirements: List[str], python_versions: List[str], venv_paths: List[str]) -> Dict[str, Dict[str, List[Tuple[bool, str]]]]:
    """Check packages across all Python versions and virtual environments."""
    results = {req: {"system": [], "venv": []} for req in requirements}
    
    # Check system-wide Python installations
    for version in python_versions:
        python_path = f"python{version}"
        for package in requirements:
            installed, version_info = check_package(package, python_path)
            results[package]["system"].append((installed, f"Python {version}: {version_info}" if installed else f"Python {version}: Not installed"))
    
    # Check virtual environments
    for venv_path in venv_paths:
        python_path = os.path.join(venv_path, "bin", "python")
        if os.path.exists(python_path):
            for package in requirements:
                installed, version_info = check_package(package, python_path)
                results[package]["venv"].append((installed, f"{venv_path}: {version_info}" if installed else f"{venv_path}: Not installed"))
    
  
    return results

def print_results(results: Dict[str, Dict[str, List[Tuple[bool, str]]]]):
    """Print the results in a formatted manner."""
    print("\n=== Package Installation Report ===\n")
    for package, environments in results.items():
        print(f"Package: {package}")
        print("  System-wide installations:")
        for installed, info in environments["system"]:
            print(f"    {'✓' if installed else '✗'} {info}")
        print("  Virtual environment installations:")
        for installed, info in environments["venv"]:
            print(f"    {'✓' if installed else '✗'} {info}")
        print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py path/to/requirements.txt")
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    if not os.path.exists(requirements_file):
        print(f"Error: File '{requirements_file}' not found.")
        sys.exit(1)
    
    requirements = read_requirements(requirements_file)
    python_versions = get_python_versions()
    venv_paths = get_virtual_env_paths()
    
    print("Checking package installations...")
    results = check_packages(requirements, python_versions, venv_paths)
    print_results(results)

if __name__ == "__main__":
    main()
