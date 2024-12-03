from config import config as cfg
import json
import os
import sys
import psycopg2
from psycopg2 import OperationalError
from colorama import Fore, Style, init
from datetime import datetime
import logging


# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class c_load_data:
    def __init__(self):
        self.db_params = cfg.PSQL_SERVER_PARAMS
        self.staging_dir = cfg.STAGING_DATA_DIR
        self.log_dir = cfg.LOG_DIR
        self.dataset_config = cfg.DATASET_CONFIG

    def process_all_files(self):
        for dataset_name in self.dataset_config:
            staging_path = os.path.join(self.staging_dir, dataset_name)
            if not os.path.exists(staging_path):
                print(
                    f"{Fore.YELLOW}No staging directory found for {dataset_name}. Skipping."
                )
                continue

            for root, _, files in os.walk(staging_path):
                for file in files:
                    if file.endswith(".json"):
                        file_path = os.path.join(root, file)
                        self.process_single_file(dataset_name, file_path)

    def process_single_file(self, dataset_name, file_path):
        try:
            # Load and insert data
            with open(file_path, "r") as file:
                json_data = json.load(file)

            stats = self.insert_json_data_to_psql(json.dumps(json_data), dataset_name)

            # Create log file
            self.create_log_file(dataset_name, file_path, success=True, stats=stats)

            # Delete original file if all data was processed
            if stats["skipped"] + stats["inserted"] + stats["updated"] == len(
                json_data
            ):
                os.remove(file_path)
                print(f"{Fore.GREEN}Successfully processed and deleted: {file_path}")
            else:
                print(
                    f"{Fore.YELLOW}File {file_path} partially processed. Not deleted."
                )

        except Exception as e:
            print(f"{Fore.RED}Error processing file {file_path}: {str(e)}")
            self.create_log_file(dataset_name, file_path, success=False, error=str(e))
            raise  # Re-raise the exception

    def insert_json_data_to_psql(self, json_data, dataset_name):
        conn = None
        stats = {"skipped": 0, "inserted": 0, "updated": 0}
        try:
            data_list = json.loads(json_data)
            if not isinstance(data_list, list):
                data_list = [data_list]

            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            for data in data_list:
                columns = ", ".join(data.keys())
                values = ", ".join(["%s"] * len(data))

                # Check if the data already exists
                check_sql = f"SELECT COUNT(*) FROM {dataset_name} WHERE id = %s"
                cursor.execute(check_sql, (data["id"],))
                if cursor.fetchone()[0] > 0:
                    # Data exists, update if necessary
                    update_sql = f"UPDATE {dataset_name} SET ({columns}) = ({values}) WHERE id = %s"
                    cursor.execute(update_sql, tuple(data.values()) + (data["id"],))
                    if cursor.rowcount > 0:
                        stats["updated"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    # Data doesn't exist, insert
                    insert_sql = (
                        f"INSERT INTO {dataset_name} ({columns}) VALUES ({values})"
                    )
                    cursor.execute(insert_sql, tuple(data.values()))
                    stats["inserted"] += 1

            conn.commit()
            logger.info(f"Data processing completed for {dataset_name}.")
            return stats

        except (json.JSONDecodeError, psycopg2.Error, Exception) as e:
            logger.error(f"Error processing data for {dataset_name}: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()

    def create_log_file(
        self, dataset_name, input_file_path, success, stats=None, error=None
    ):
        log_time = datetime.now().strftime("%Y%m%d")
        relative_path = os.path.relpath(input_file_path, self.staging_dir)
        log_dir = os.path.join(self.log_dir, "load", os.path.dirname(relative_path))

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file_name = f"{datetime.now().strftime('%H%M')}.json"
        log_file_path = os.path.join(log_dir, log_file_name)

        log_data = {
            "input_file": input_file_path,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "stats": stats,
        }

        with open(log_file_path, "w") as log_file:
            json.dump(log_data, log_file, indent=2)


# Example usage
if __name__ == "__main__":
    loader = c_load_data()
    loader.process_all_files()
