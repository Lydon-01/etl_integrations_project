from src.etl_integrations_project_lydon.extract.c_extract_data import (
    c_extract_data,
)
import unittest


class TestCExtractData(unittest.TestCase):
    def test_initialization(self):
        """
        Test if the c_extract_data class can be instantiated
        without raising any errors or returning null.
        """
        try:
            # Provide dummy arguments for the
            # constructor
            transformer = c_extract_data(
                dataset_config={},
                base_url="https://example.com/api/",
                headers={"Authorization": "Bearer dummy-token"},
                output_dir="/tmp/data",
            )
            self.assertIsNotNone(transformer, "The class instantiation returned None.")
        except Exception as e:
            self.fail(
                f"c_extract_data raised an exception during instantiation: {str(e)}"
            )

    # There should be unit tests for each function in the class.


if __name__ == "__main__":
    unittest.main()
