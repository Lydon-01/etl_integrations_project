from src.etl_integrations_project_lydon.load.c_load_data import c_load_data
import unittest


class TestCLoadData(unittest.TestCase):
    def test_initialization(self):
        """
        Test if the class can be instantiated without raising any errors or returning null.
        """
        try:
            transformer = c_load_data()
            self.assertIsNotNone(transformer)
        except Exception as e:
            self.fail(f"Initialization failed with error: {str(e)}")

    # There should be unit tests for each function in the class.


if __name__ == "__main__":
    unittest.main()
