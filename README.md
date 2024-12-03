```
                            ++                                                   
     %%%%%%%%    %%%%%%%%    +++   ++   ++    +++    +++++     ++     +++++      
         %%%     %%         %  +++ ++    ++  ++    ++    +     ++   ++    ++     
        %%%     %%%%%%%     %%%  ++++     ++++     ++++++      ++   ++++++       
       %%        %%         %%%%%  ++      ++           +++    ++        +++     
      %%         %%         %%  %%%        ++      ++    ++    ++   ++    ++     
     %%%%%%%%    %%%%%%%%   %%    %%%      ++        ++++      ++     ++++       
                                    %%                                           
```
# etl Integration Project
by Lydon Carter, Q4 2024

## Overview

This project implements an ETL (Extract, Transform, Load) pipeline that extracts data from the WHO GHO OData API, processes it, and loads it into a PostgreSQL database. The pipeline is built using Python and focuses on efficiency, reliability, and extensibility.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Features](#features)
- [Testing](#testing)
- [Notes](#notes)

## Prerequisites

- Python 3.7+
- PostgreSQL server with database
- Prefer Unix environment (code tested on RHEL AL2)
- For limitations, check the [Notes](#notes)

## Installation

1. Download and unzip the package (note in a prod system you would use 'git clone' of the repository). Open your terminal and change to the new path:
   ```
   cd ~/Downloads/etl_integrations_project_lydon
   ```

2. (Recommended) Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Set your `PYTHONPATH` to the root of the directory. Example for Linux via terminal:
   ```
   export PYTHONPATH=$PYTHONPATH:$(pwd)

   # To persist for your virtual env: 
   echo 'export PYTHONPATH=$PYTHONPATH:$(pwd)' >> venv/bin/activate

   echo $PYTHONPATH
   ```

4. Install requirements:
   ```
   python3 utils/install_requirements.py
   ```

## Configuration

1. Modify PostgreSQL database parameters:
   - Add your details in the `.env` variables (used in the `config.py`).
   - **Note**: To make use of the owner's RDS database, please reach out with your public IP or CIDR to be allowed access. 

2. (Optional) Adjust other configuration parameters in `config.py` if needed.

## Usage

1. Run all tests:
   ```
   python3 run_tests.py
   ```
   - **Note**: There is a known bug with `test_requirements` not detecting installed packages. Check your `install_requirements` to verify packages were installed. 
   - **Note**: If this is your first run, the destination `dataset table name` would not yet exist. After the `start_load.py` it should be created. 

2. Start the ETL pipeline:
   - To run the entire scheduler:
     ```
     python3 scripts/start_scheduler.py
     ```
   - To run individual steps:
     ```
     python3 scripts/start_extract.py
     python3 scripts/start_transform.py
     python3 scripts/start_load.py
     ```
   - The respective data is temporarily stored until processed. i.e. 
     - First Extract will create Landing data, and Transform will create Staging data, and lastly we call Load. 
     - Each successful call will delete the previous phase of data that was processed. 

3. Check the `logs/` directory for operation information.

4. Verify data by connecting to your database and sampling the data:
   - You can re-run the PSQL test script: 
     ```
     python3 tests/test_c_psql.py
     ```
   - OR you can connect using your own tool and query: 
     ```
     SELECT * FROM life_expectancy_at_birth LIMIT 10;
     ```

5. Stop all scheduled tasks:
   ```
   python3 scripts/stop_scheduler.py
   ```

6. For cleanup, delete the `logs/` and `data/` folders. 

7. If used, stop the Python virtual environment:
   ```
   deactivate
   ```

8. (Optional) Clean the cache files. Linux example:
   ```
   find . -type d -name "__pycache__" -exec rm -rf {} +
   ```

## Project Structure

The components of the project are designed in a modular way for future expansion. 
```
etl_integrations_project_lydon/
│
├── config/
│   └── config.py
├── data/
├── logs/
├── scripts/
│   ├── start_extract.py
│   ├── start_transform.py
│   ├── start_load.py
│   └── start_scheduler.py
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── scheduler.py
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── utils/
│   ├── format_code.py
│   └── install_requirements.py
├── README.md
└── requirements.txt
```

## Features

- Modular ETL pipeline
- Configurable data source and indicators
- Error handling and logging
- Data validation
- Resumable operations
- Duplicate data prevention

## Testing

Run all tests with:
```
python3 run_tests.py
```

For individual test files:
```
python3 tests/test_<module>.py
```

## Notes

### Versioning
- Version control not implemented for this dev project. S3 backup utility created instead.

### Style Standards
- Using `flake8` for quality and `black` for style.
- Run `python3 utils/format_code.py` to auto-format the code.
- A GenAI assistant was used, use discretion for inconsistencies in code. 

### Database
- Modify `config.PSQL_SERVER_PARAMS` for your database connection.
- Schema evolution feature included (see `alter_table_` function).

### Logging
- Logs stored as JSON in `logs/` directory.
- Consider implementing log rotation or cleanup for production use.

### Local Imports
- Run scripts from the project root directory.
- PYTHONPATH must be set in your environment or IDE settings. For VSCode, you would use: `Open User Settings (JSON)`

### Scheduling 
- The `conf.py` has `DATASET_CONFIG` with jobs to execute. These jobs can be enabled and disabled. (Feel free to do so)

### Dataset config 
- Currently only one source dataset is defined ("life_expectancy_at_birth"). The `DATASET_CONFIG` is designed so that additional datasets can be added, or filters changed, or schema modified. 

## Future recommendations 
I would recommend utilizing the Cloud for this ETL requirement. It would ensure: 
- Maximum processing scalability 
- Increased stability and security
- Managed services to avoid complexity and improve monitoring
- Minimize operational burden
- Provide access to latest features and add flexibility

### An example AWS 
- Amazon EC2 instance to host and run the Python ETL application
- Amazon S3 bucket for temporary storage of extracted data
- AWS Lambda for triggering the ETL process on a schedule
- Amazon RDS for PostgreSQL as the target database
- Amazon CloudWatch for monitoring and logging
- AWS IAM for managing access and permissions
- Amazon SNS for notifications on ETL job status
- AWS Step Functions (optional) for orchestrating the ETL workflow

---

For any questions or issues, please open an issue in the project repository.