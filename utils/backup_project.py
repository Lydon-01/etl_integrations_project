import fnmatch
import concurrent.futures
import sys
import os
import json
import logging
from datetime import datetime
import boto3
from tqdm import tqdm

sys.path.append(os.getcwd())
from config import config as cfg  # noqa: E402


class ProjectBackup:
    def __init__(self):
        self.config = cfg.BACKUP_CONFIG["s3"]
        self.log_config = cfg.BACKUP_CONFIG["logging"]
        self.local_source = self.config["local_source"]
        self.s3_bucket = self.config["s3_bucket"]
        self.region = self.config["region"]
        self.max_workers = self.config["max_workers"]
        self.exclude_patterns = self.config["exclude_patterns"]
        self.s3_client = boto3.client("s3", region_name=self.region)
        self.logger = self._setup_logger()
        self.datehour = datetime.now().strftime("%Y%m%d%H%M")
        self.s3_base_path = self.config["s3_base_path"].format(datehour=self.datehour)

        # Update the backup_log_path to match the desired structure without hyphens
        log_date = self.datehour[:8]  # YYYYMMDD
        log_time = self.datehour[8:]  # HHMM
        self.backup_log_path = os.path.join(
            self.log_config["log_dir"],
            self.log_config["log_subdir"],
            log_date,
            f"{log_time}.json",
        )

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create a formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(ch)

        return logger

    def _should_exclude(self, file_path):
        return any(
            fnmatch.fnmatch(file_path, pattern) for pattern in self.exclude_patterns
        )

    def _get_all_files(self):
        all_files = []
        for root, _, files in os.walk(self.local_source):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, self.local_source)
                if not self._should_exclude(relative_path):
                    s3_file_path = os.path.join(self.s3_base_path, relative_path)
                    all_files.append((local_file_path, s3_file_path))
        return all_files

    def run_backup(self):
        all_files = self._get_all_files()
        total_files = len(all_files)
        results = {"successful": 0, "failed": 0}

        with tqdm(
            total=total_files, desc="Uploading files", unit="file", ncols=100
        ) as pbar:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            ) as executor:
                future_to_file = {
                    executor.submit(self._upload_file, local_path, s3_path): (
                        local_path,
                        s3_path,
                    )
                    for local_path, s3_path in all_files
                }

                for future in concurrent.futures.as_completed(future_to_file):
                    local_path, s3_path = future_to_file[future]
                    try:
                        if future.result():
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        self._log_error(
                            f"Failed to upload {local_path} to {s3_path}: {str(e)}"
                        )
                    finally:
                        pbar.update(1)

        self._log_backup_result(results["successful"], results["failed"], total_files)

    def _upload_file(self, local_file_path, s3_file_path):
        try:
            self.s3_client.upload_file(local_file_path, self.s3_bucket, s3_file_path)
            return True
        except Exception as e:
            self._log_error(
                f"Failed to upload {local_file_path} to {s3_file_path}: {str(e)}"
            )
            return False

    def _log_error(self, message):
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def _log_backup_result(self, successful, failed, total):
        log_data = {
            "timestamp": self.datehour,
            "successful": successful,
            "failed": failed,
            "total": total,
        }

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.backup_log_path), exist_ok=True)

        # Write the log data to the JSON file
        try:
            with open(self.backup_log_path, "w") as f:
                json.dump(log_data, f, indent=2)
            self._log_info(
                f"Backup completed. Results logged to {self.backup_log_path}"
            )
        except Exception as e:
            self._log_error(f"Failed to write log to {self.backup_log_path}: {str(e)}")

    def _log_info(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")


# Call it
if __name__ == "__main__":
    backup = ProjectBackup()
    backup.run_backup()
