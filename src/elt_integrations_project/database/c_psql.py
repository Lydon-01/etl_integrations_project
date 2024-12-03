import sys
import os
import json
import psycopg2
from psycopg2 import pool
from colorama import Fore, init
from datetime import datetime

sys.path.append(os.getcwd())
from config import config as cfg

init(autoreset=True)

db_params = cfg.PSQL_SERVER_PARAMS


class c_psql:
    def __init__(self, params=db_params):
        self.params = params
        self.conn_pool = None
        self.log_data = []
        self.create_database_if_not_exists()
        self.create_connection_pool()

    def create_database_if_not_exists(self):
        try:
            # Connect to default 'postgres' database to create new database
            conn = psycopg2.connect(
                host=self.params["host"],
                user=self.params["user"],
                password=self.params["password"],
                port=self.params["port"],
                database="postgres",
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(
                f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.params['database']}'"
            )
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.params['database']}")
                self.log_action(
                    f"Database '{self.params['database']}' created successfully."
                )

            cursor.close()
            conn.close()
        except Exception as e:
            self.log_action(f"Error creating database: {e}", level="ERROR")
            sys.exit(1)

    def create_connection_pool(self):
        try:
            self.conn_pool = psycopg2.pool.SimpleConnectionPool(
                1,
                5,
                host=self.params["host"],
                dbname=self.params["database"],
                user=self.params["user"],
                password=self.params["password"],
                port=self.params["port"],
            )
            if self.conn_pool:
                self.log_action("Connection pool created successfully.")
        except Exception as e:
            self.log_action(f"Error creating connection pool: {e}", level="ERROR")
            sys.exit(1)

    def create_table_from_schema(self, dataset_name, conn):
        dataset = cfg.DATASET_CONFIG.get(dataset_name)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found in config.")

        schema = dataset.get("staging_schema")
        table_name = schema.get("table_name")
        columns = schema.get("columns")

        column_definitions = ", ".join(
            [f"{col_name} {col_type}" for col_name, col_type in columns]
        )
        create_table_sql = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"
        )

        try:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
                self.log_action(f"Table '{table_name}' created successfully.")
            self.alter_table_for_schema(dataset_name, conn)
        except Exception as e:
            self.log_action(f"Error creating table '{table_name}': {e}", level="ERROR")
            conn.rollback()

    def alter_table_for_schema(self, dataset_name, conn):
        dataset = cfg.DATASET_CONFIG.get(dataset_name)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found in config.")

        schema = dataset.get("staging_schema")
        table_name = schema.get("table_name")
        columns = schema.get("columns")

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"
                )
                current_columns = cursor.fetchall()

            current_column_names = {col[0] for col in current_columns}
            desired_column_names = {col[0] for col in columns}

            for col_name, col_type in columns:
                if col_name not in current_column_names:
                    alter_sql = (
                        f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
                    )
                    with conn.cursor() as cursor:
                        cursor.execute(alter_sql)
                        conn.commit()
                        self.log_action(
                            f"Added column '{col_name}' to table '{table_name}'."
                        )
        except Exception as e:
            self.log_action(f"Error altering table '{table_name}': {e}", level="ERROR")
            conn.rollback()

    def log_action(self, message, level="INFO"):
        self.log_data.append(
            {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
            }
        )

    def save_logs(self):
        log_dir = os.path.join(cfg.LOG_DIR, "psql")
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M")
        log_file = os.path.join(log_dir, f"{date_str}", f"{time_str}.json")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, "w") as f:
            json.dump(self.log_data, f, indent=2)

    def create_all_tables(self):
        conn = self.conn_pool.getconn()
        try:
            for dataset_name in cfg.DATASET_CONFIG:
                self.create_table_from_schema(dataset_name, conn)
        finally:
            self.conn_pool.putconn(conn)


if __name__ == "__main__":
    psql = c_psql()
    psql.create_all_tables()
    psql.save_logs()
