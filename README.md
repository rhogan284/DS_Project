
# Airport Data ETL Pipeline

## Overview

This repository contains a university project that defines a data generator and ETL (Extract, Transform, Load) pipeline to transport generated airport data to a Google Cloud MySQL database. The project involves creating synthetic data representing airport operations and utilizing various scripts to process and load this data into the cloud database.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [User Interface](#user-interface)
- [End ETL Process](#end-etl-process)

## Project Structure

The repository contains the following main files:

- `data_stream_v2.py`: Script for generating synthetic airport data.
- `export_sql.py`: Script for exporting data to a Google Cloud MySQL database.
- `export_sql+bq.py`: Script for exporting data to both Google Cloud MySQL and BigQuery.
- `DF RUN WIN - SQL`: Script for running the ETL pipeline targeting SQL.
- `DF RUN WIN - SQL + BQ`: Script for running the ETL pipeline targeting both SQL and BigQuery.
- `home.py`: Flask application for interfacing with the database and Google Looker for reporting.


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
5. **Create a Google Cloud Pub/Sub Topic and Subscription**:
    - Create a Pub/Sub topic:
      ```sh
      gcloud pubsub topics create your-topic-name
      ```
    - Create a Pub/Sub subscription:
      ```sh
      gcloud pubsub subscriptions create your-subscription-name --topic=your-topic-name
      ```
    - Fill in the relevant details in the dataflow run commands within the scripts, specifying the topic and subscription names.
  
   
6. **Set up a Cloud MySQL Instance**:
    - Create a Cloud SQL instance:
      ```sh
      gcloud sql instances create your-instance-name --database-version=MYSQL_5_7 --tier=db-n1-standard-1 --region=your-region
      ```
    - Set a password for the root user:
      ```sh
      gcloud sql users set-password root --host=% --instance=your-instance-name --password=your-password
      ```
    - Connect to your instance and create a database:
      ```sh
      gcloud sql connect your-instance-name --user=root
      mysql> CREATE DATABASE your-database-name;
      ```
    - Run the SQL script found at `setup.sql` on the database to set up the necessary tables:
      ```sh
      mysql -u root -p your-database-name < setup.sql
      ```
    - Fill in the relevant details in the config file, specifying the database connection details (instance name, database name, user, password).


7. **Import fixed data to MySQL database**:
   - Create a Cloud Storage Bucket: 
      ```sh
      gcloud storage buckets create gs://BUCKET_NAME --location=BUCKET_LOCATION
      ```
   - Upload each entity csv file to the bucket:
      ```sh
      gcloud storage cp ENTITY_LOCATION gs://DESTINATION_BUCKET_NAME
      ```
   - Import each csv file to the associated database table:
      ```sh
      gcloud sql import csv INSTANCE_NAME gs://BUCKET_NAME/FILE_NAME \
      --database=DATABASE_NAME \
      --table=TABLE_NAME
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

### User Interface 

The project includes a Flask application (home.py) that serves as a user interface for interacting with the database and Google Looker for reporting. The Flask app provides the following functionalities:

- **User Authentication**: Users can log in with their credentials to access the application. 
- **Flight Data Viewing**: Authenticated users can view flight data, including flight IDs, statuses, airports, and times. 
- **Ticket Data Viewing**: Authenticated users can view ticket data associated with a flight, including the passenger details, seat number and flight ID. 
- **Google Looker Integration**: The app connects to Google Looker for reporting and data visualization.

To run the Flask app:

```sh
export FLASK_APP=home.py
flask run
```
Navigate to http://127.0.0.1:8000/ in your web browser to access the application.

### Stop ETL Process

To stop the ETL process complete the following steps in order:

1. Stop `data_stream_v2.py` script
2. Drain dataflow job:
   ```sh
   gcloud dataflow jobs drain JOB_ID
   ```
3. Purge remaining messages in Pub/Sub by seeking to a future time:
   ```sh
   gcloud pubsub subscriptions seek SUBSCRIPTION_ID \
    --time=TIME \
   ```