
# Airport Data ETL Pipeline

## Overview

This repository contains a university project that defines a data generator and ETL (Extract, Transform, Load) pipeline to transport generated airport data to a Google Cloud MySQL database. The project involves creating synthetic data representing airport operations and utilizing various scripts to process and load this data into the cloud database.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Files](#files)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

The repository contains the following main files:

- `data_stream_v2.py`: Script for generating synthetic airport data.
- `export_sql.py`: Script for exporting data to a Google Cloud MySQL database.
- `export_sql+bq.py`: Script for exporting data to both Google Cloud MySQL and BigQuery.
- `DF RUN WIN - SQL`: Script for running the ETL pipeline targeting SQL.
- `DF RUN WIN - SQL + BQ`: Script for running the ETL pipeline targeting both SQL and BigQuery.

## Requirements

To run this project, you will need:

- Python 3.6 or higher
- Google Cloud SDK
- MySQL database on Google Cloud
- BigQuery on Google Cloud

Required Python packages can be installed using the `requirements.txt` file.

## Setup

1. Clone this repository:
    ```sh
    git clone https://github.com/rhogan284/EfficientSky.git
    cd airport-data-etl
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up your Google Cloud project and enable the necessary APIs (Cloud SQL, BigQuery).

4. Configure your Google Cloud authentication by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
    ```sh
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
    ```

## Usage

### Generating Data

To generate synthetic airport data, run:
```sh
python data_stream_v2.py
```

### Running the ETL Pipeline

For running the ETL pipeline targeting SQL:
```sh
python export_sql.py
```

For running the ETL pipeline targeting both SQL and BigQuery:
```sh
python export_sql+bq.py
```
