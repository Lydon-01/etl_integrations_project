from config import config as cfg
import psycopg2
from psycopg2 import OperationalError
from colorama import Fore, init
import unittest

init(autoreset=True)

class PostgresTester(unittest.TestCase):
    def setUp(self):
        """Set up database parameters for the test cases."""
        self.db_params = cfg.PSQL_SERVER_PARAMS

    def execute_query(self, query, fetch=True):
        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    if fetch:
                        result = cursor.fetchall()
                        description = cursor.description
                        return result, description
                    return None, None
        except OperationalError as e:
            print(Fore.RED + f"Database error: {e}")
            return None, None
        except Exception as e:
            print(Fore.YELLOW + f"Query execution failed: {e}")
            return None, None

    def test_connection(self):
        """Test the database connection."""
        result, _ = self.execute_query("SELECT version();")
        self.assertIsNotNone(result, "Database connection failed.")
        print(Fore.GREEN + "Connection successful!")
        print(Fore.CYAN + f"PostgreSQL version:")
        print(Fore.YELLOW + result[0][0] + "\n")

    def test_list_databases(self):
        """Test retrieving the list of databases."""
        query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
        databases, _ = self.execute_query(query)
        self.assertIsNotNone(databases, "Failed to retrieve database list.")
        print(Fore.CYAN + "Databases on the server:")
        for db in databases:
            print(Fore.YELLOW + db[0])
        print("\n")

    def test_list_tables(self):
        """Test retrieving the list of tables."""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
        """
        tables, _ = self.execute_query(query)
        self.assertIsNotNone(tables, "Failed to retrieve table list.")
        print(Fore.CYAN + "Tables in the current database:")
        for table in tables:
            print(Fore.YELLOW + table[0])
        print("\n")

    def test_table_structure(self):
        """Test the structure of a specific table and print sample data."""
        # InHardcoded. In future must run for each table in the Config.
        table_name = "life_expectancy_at_birth"  
        query = f"SELECT * FROM {table_name} LIMIT 5;"
        result, description = self.execute_query(query)
        
        self.assertIsNotNone(result, f"Unable to access table '{table_name}'. Maybe it's not created yet")
        print(Fore.GREEN + f"Table '{table_name}' exists and is accessible.")
        
        if result and description:
            # Get column names
            column_names = [desc[0] for desc in description]
            
            # Print column names
            print("\nSample data:")
            print(" | ".join(column_names))
            print("-" * (sum(len(name) for name in column_names) + 3 * (len(column_names) - 1)))
            
            # Print rows
            for row in result:
                print(" | ".join(str(value) for value in row))
        else:
            print(Fore.RED + "No data retrieved from the table.")

# Run the tests
if __name__ == "__main__":
    unittest.main()
