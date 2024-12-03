import subprocess
import importlib
import sys
print(sys.path)
from tests.test_requirements import TestRequirements

def install_setuptools():
    try:
        # Check if setuptools is already installed
        import pkg_resources
        print("setuptools is already installed.")
        
        # Attempt to upgrade setuptools
        print("Attempting to upgrade setuptools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"])
        print("setuptools has been successfully upgraded.")
    
    except ImportError:
        # If setuptools is not installed, install it
        print("setuptools is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
        print("setuptools has been successfully installed.")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing/upgrading setuptools: {e}")
        sys.exit(1)


def install_requirements():
    """Install Python packages from requirements.txt."""
    try:
        print("Installing requirements...")
        subprocess.check_call(
            #  Can also be harcoded to ["python3", "-m", 
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Current sys.path:")
    for path in sys.path:
           print(path)
    print("\n")
    install_setuptools()
    install_requirements()
    
    # Reload sys.path
    import site
    importlib.reload(site)
    
    TestRequirements.test_requirements(None)
