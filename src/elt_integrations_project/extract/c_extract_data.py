import sys
import requests
import os
import json
import time
from datetime import datetime
from colorama import Fore, init

sys.path.append(os.getcwd())
from config import config as cfg  # noqa: E402

# Initialize colorama
init(autoreset=True)


class c_extract_data:
    def __init__(self, dataset_config, base_url, headers, output_dir):
        self.base_url = base_url
        self.headers = headers
        self.dataset_config = dataset_config
        self.output_dir = output_dir

    def construct_filter_query(self, filters):
        """
        Constructs the OData filter query string based on the filters dictionary.
        """
        filter_clauses = []
        for key, values in filters.items():
            if isinstance(values, list):
                # Assuming array values imply 'or' clauses in the filter
                filter_part = " or ".join([f"{key} eq '{value}'" for value in values])
                if len(values) > 1:
                    filter_part = f"({filter_part})"
            else:  # For single-value filters like a date
                filter_part = f"{key} ge '{values}'"
            filter_clauses.append(filter_part)

        return " and ".join(filter_clauses)

    def get_data(self, indicator_key):
        # Get indicator configuration based on the
        # key
        indicator_config = self.dataset_config.get(indicator_key)

        if not indicator_config:
            raise ValueError(
                f"{Fore.RED}Indicator '{indicator_key}' not found in the extraction config.{Fore.RESET}"
            )

        # Construct the base URL
        indicator_code = indicator_config["code"]
        url = f"{self.base_url}{indicator_code}"

        # Construct the filter query
        filters = indicator_config.get("filters", {})
        filter_query = self.construct_filter_query(filters)
        params = {"$filter": filter_query}

        # Fetch the data from the API
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(
                f"{Fore.RED}Failed to fetch data: {response.status_code} - {response.text}{Fore.RESET}"
            )

        # Generate the current date and time for the filename and directory structure
        current_time = datetime.now()
        year_month_day = current_time.strftime("%Y%m%d")
        hour_minute = current_time.strftime("%H%M")

        # Create the path in the format 'data/landing/key/yyymmdd/'
        indicator_dir = os.path.join(self.output_dir, indicator_key, year_month_day)
        if not os.path.exists(indicator_dir):
            os.makedirs(indicator_dir)

        # Store the data to a file named as HHmm.json
        output_file = os.path.join(indicator_dir, f"{hour_minute}.json")

        with open(output_file, "w") as f:
            json.dump(response.json(), f, indent=4)

        print(
            f"{Fore.GREEN}Data for {indicator_key} saved to {output_file}{Fore.RESET}"
        )


# Main block to run the extractor if executed as a
# script
if __name__ == "__main__":
    extractor = c_extract_data(
        dataset_config=cfg.DATASET_CONFIG,
        base_url=cfg.BASE_API_URL,
        headers=cfg.HEADERS,
        output_dir=cfg.LANDING_DATA_DIR,
    )

    # Example: Get data for
    # 'life_expectancy_at_birth'
    extractor.get_data("life_expectancy_at_birth")
