
import importlib
import pkg_resources
import unittest


class TestRequirements(unittest.TestCase):
    """Test that each required package is available."""

    def test_requirements(self):
        # Read requirements file
        try:
            with open("requirements.txt") as f:
                requirements_content = f.read()
        except FileNotFoundError:
            self.fail("requirements.txt not found. Please ensure the file exists.")

        # Parse the requirements from the content of the file
        requirements = pkg_resources.parse_requirements(
            requirements_content.splitlines()
        )

        # Track failed packages
        missing_packages = []

        # Try to import each required package
        print("\nChecking required packages:\n")
        print(f"{'Package':<30}{'Status':<10}")
        print("-" * 40)
        for package in requirements:
            package_name = str(package).split("==")[0]
            try:
                importlib.import_module(package_name)
                print(f"{package_name:<30}{'OK':<10}")
            except ImportError:
                print(f"{package_name:<30}{'MISSING':<10}")
                missing_packages.append(str(package))

        # Assert that there are no missing packages
        if missing_packages:
            print("\nThe following packages are missing:\n")
            print(f"{'Package':<30}{'Version Requirement':<20}")
            print("-" * 50)
            for package in missing_packages:
                package_name, _, version = package.partition("==")
                print(f"{package_name:<30}{version:<20}")

            print("\nTo install the missing packages, run:")
            print("  pip3 install -r requirements.txt\n")
            raise AssertionError(f"Missing packages: {', '.join(missing_packages)}")
        else:
            print("\nAll required packages are installed.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
