import json
import os
import sys
import polars as pl
from colorama import Fore, Style, init
from datetime import datetime

sys.path.append(os.getcwd())
from config import config as cfg  # noqa: E402

# Initialize colorama
init(autoreset=True)


class c_transform_data:
    def __init__(self):
        self.data = None
        self.dataset_config = cfg.DATASET_CONFIG
        self.landing_dir = cfg.LANDING_DATA_DIR
        self.staging_dir = cfg.STAGING_DATA_DIR
        self.log_dir = cfg.LOG_DIR

    def process_all_files(self):
        for dataset_name in self.dataset_config:
            landing_path = os.path.join(self.landing_dir, dataset_name)
            if not os.path.exists(landing_path):
                print(
                    f"{Fore.YELLOW}No landing directory found for {dataset_name}. Skipping."
                )
                continue

            for root, _, files in os.walk(landing_path):
                for file in files:
                    if file.endswith(".json"):
                        file_path = os.path.join(root, file)
                        self.process_single_file(dataset_name, file_path)

    def process_single_file(self, dataset_name, file_path):
        try:
            # Load data
            self.get_data_file(file_path)

            # Transform data
            transformed_data = self.transform_data()

            if transformed_data is not None:
                # Save transformed data
                output_path = self.save_data(dataset_name, file_path)

                if output_path:
                    # Create log file
                    self.create_log_file(
                        dataset_name, file_path, output_path, success=True
                    )

                    # Delete original file
                    os.remove(file_path)
                    print(
                        f"{Fore.GREEN}Successfully processed and deleted: {file_path}"
                    )
                else:
                    self.create_log_file(dataset_name, file_path, None, success=False)
            else:
                self.create_log_file(dataset_name, file_path, None, success=False)

        except Exception as e:
            print(f"{Fore.RED}Error processing file {file_path}: {str(e)}")
            self.create_log_file(
                dataset_name, file_path, None, success=False, error=str(e)
            )

    def get_data_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                value_data = json_data.get("value", [])

                if not value_data:
                    raise ValueError(
                        f"No 'value' key found in the JSON file: {file_path}"
                    )

            self.data = pl.DataFrame(value_data)
            return self.data

        except Exception as e:
            print(f"{Fore.RED}Error loading data: {str(e)}")
            return None

    def transform_data(self):
        try:
            # Get current epoch time in seconds
            current_epoch = int(datetime.now().timestamp())

            self.data = self.data.with_columns(
                [
                    pl.col("SpatialDim").alias("country"),
                    pl.col("Dim1").alias("sex"),
                    pl.lit(current_epoch).alias("transformed_epoch"),
                    pl.col("NumericValue").cast(pl.Float64),
                    pl.col("TimeDim").cast(pl.Int64),
                    pl.col("Date")
                    .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f%z")
                    .dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    pl.col("TimeDimensionBegin")
                    .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%z")
                    .dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    pl.col("TimeDimensionEnd")
                    .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%z")
                    .dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                ]
            )

            columns_to_drop = [
                "Dim2Type",
                "Dim2",
                "Dim3Type",
                "Dim3",
                "DataSourceDimType",
                "DataSourceDim",
                "Value",
                "High",
                "Low",
                "SpatialDimType",
            ]
            self.data = self.data.drop(
                [col for col in columns_to_drop if col in self.data.columns]
            )

            self.data = self.data.rename(
                {col: col.lower() for col in self.data.columns}
            )

            return self.data

        except Exception as e:
            print(f"{Fore.RED}Error during transformation: {str(e)}")
            return None

    def save_data(self, dataset_name, input_file_path):
        indicator_config = self.dataset_config.get(dataset_name)
        if not indicator_config:
            raise ValueError(
                f"{Fore.RED}Indicator '{dataset_name}' not found in the extraction config.{Fore.RESET}"
            )

        current_time = datetime.now()
        hour_minute = current_time.strftime("%H%M")

        relative_path = os.path.relpath(input_file_path, self.landing_dir)
        output_dir = os.path.join(self.staging_dir, os.path.dirname(relative_path))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file_path = os.path.join(output_dir, f"{hour_minute}.json")

        rows = self.data.to_dicts()

        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
            return output_file_path
        except Exception as e:
            print(f"{Fore.RED}Error saving data: {str(e)}")
            return None

    def create_log_file(
        self, dataset_name, input_file_path, output_file_path, success, error=None
    ):
        log_time = datetime.now().strftime("%Y%m%d")
        relative_path = os.path.relpath(input_file_path, self.landing_dir)
        log_dir = os.path.join(
            self.log_dir, "transform", os.path.dirname(relative_path)
        )

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file_name = f"{os.path.splitext(os.path.basename(input_file_path))[0]}.json"
        log_file_path = os.path.join(log_dir, log_file_name)

        log_data = {
            "input_file": input_file_path,
            "output_file": output_file_path,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "schema": self.get_schema_str() if success else None,
        }

        with open(log_file_path, "w") as log_file:
            json.dump(log_data, log_file, indent=2)

    def get_schema_str(self):
        if self.data is None or not isinstance(self.data, pl.DataFrame):
            return "Invalid DataFrame"
        return str(self.data.schema)


# Example usage
if __name__ == "__main__":
    transformer = c_transform_data()
    transformer.process_all_files()
