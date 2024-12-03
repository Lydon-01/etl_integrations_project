import os
from dotenv import load_dotenv

# API Config
BASE_API_URL = "https://ghoapi.azureedge.net/api/"
HEADERS = {"Content-type": "application/json"}

# Project Dir Config
ROOT_DIR = os.getcwd()
LANDING_DATA_DIR = os.path.join(ROOT_DIR, "data/landing")  # raw or minimally processed
STAGING_DATA_DIR = os.path.join(
    ROOT_DIR, "data/staging"
)  # transformed and ready for upload/use
LOG_DIR = os.path.join(ROOT_DIR, "logs")


# PSQL config
load_dotenv()
PSQL_SERVER_PARAMS = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT'),
    "database": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),  # Plain text ONLY in local dev!
    "connect_timeout": 5,
}


DATASET_CONFIG = {
    "life_expectancy_at_birth": {
        "DataFreshnessDays": 3650,
        "name": "Life expectancy at birth (years)",
        "code": "WHOSIS_000001",
        "filters": {
            "SpatialDim": [  # Southern African Countries
                "ZAF",
                "BWA",
                "NAM",
                "ZWE",
                "MOZ",
                "LSO",
            ]
        },
        "sample_landing_file": "/local/home/carlydon/dev/etl_integrations_project_lydon_v2/data/landing/life_expectancy_at_birth/20241201/1319.json",
        "sample_staging_file": "/local/home/carlydon/dev/etl_integrations_project_lydon_v2/data/staging/life_expectancy_at_birth/20241201/1603.json",
        "staging_schema": {
            "table_name": "life_expectancy_at_birth",
            "columns": [
                ("id", "SERIAL PRIMARY KEY"),
                ("indicatorcode", "VARCHAR(20)"),
                ("spatialdim", "VARCHAR(3)"),
                ("parentlocationcode", "VARCHAR(3)"),
                ("timedimtype", "VARCHAR(10)"),
                ("parentlocation", "VARCHAR(50)"),
                ("dim1type", "VARCHAR(10)"),
                ("timedim", "INTEGER"),
                ("dim1", "VARCHAR(10)"),
                ("numericvalue", "FLOAT"),
                ("comments", "TEXT"),
                ("date", "TIMESTAMP"),
                ("timedimensionvalue", "VARCHAR(4)"),
                ("timedimensionbegin", "TIMESTAMP"),
                ("timedimensionend", "TIMESTAMP"),
                ("country", "VARCHAR(3)"),
                ("sex", "VARCHAR(10)"),
                ("transformed_epoch", "BIGINT"),
                ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ],
        },
    }
}

# Schedule_tasks config
SCHEDULE_CONFIG = {
    "start_delay_seconds": 5,
    "jobs": {
        # Auto-kill, uncomment for added safety
        # "stop_scheduler": {"frequency": "daily", "path": "scripts/stop_scheduler.py"},
        # Helpers
        # "backup_project": {"frequency": "hourly", "path": "utils/backup_project.py"},
        # "format_code": {"frequency": "daily", "path": "utils/c_format_code.py"},
        "start_psql": {"frequency": "weekly", "path": "scripts/start_psql.py"},
        # The ETL
        "start_extract": {"frequency": "hourly", "path": "scripts/start_extract.py"},
        "start_transform": {
            "frequency": "hourly",
            "path": "scripts/start_transform.py",
        },
        "start_load": {"frequency": "hourly", "path": "scripts/start_load.py"},
    },
}

# Backup utility config
BACKUP_CONFIG = {
    "s3": {
        "region": "af-south-1",
        "s3_bucket": "lydon-aws-cpt",
        "local_source": ".",
        "s3_base_path": "backups/etl/integrations_project_lydon_{datehour}",
        "max_workers": 8,
        "exclude_patterns": [".git/*", "*.pyc", "__pycache__/*"],
    },
    "logging": {
        "log_dir": LOG_DIR,
        "log_subdir": "backup_project",
    },
}
