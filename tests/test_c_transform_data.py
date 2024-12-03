from src.etl_integrations_project_lydon.transform.c_transform_data import (
    c_transform_data,
)
import unittest


class TestCTransformData(unittest.TestCase):
    def test_initialization(self):
        """
        Test if the c_transform_data class can be instantiated without raising any errors or returning null.
        """
        try:
            transformer = c_transform_data()
            self.assertIsNotNone(transformer)
        except Exception as e:
            self.fail(f"Initialization failed with error: {str(e)}")

    # There should be unit tests for each function in the class.


if __name__ == "__main__":
    unittest.main()
