import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam import Pipeline
from apache_beam import Row
from apache_beam.io import ReadFromPubSub, WriteToBigQuery, BigQueryDisposition
from apache_beam.io.jdbc import WriteToJdbc

logging.getLogger().setLevel(logging.INFO)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Other + Old Scripts/data-systems-assignment-a8059c08d52e.json"

SCHEMA = ('Flight_ID:STRING, Flight_Status:STRING, Aircraft_ID:STRING, Model_ID:STRING, Destination_Airport:STRING, '
          'Departure_Airport:STRING, Departure_Time:TIMESTAMP, Arrival_Time:TIMESTAMP, Passport_No:STRING, '
          'Seat_No:INTEGER')

JDBC_URL = 'jdbc:mysql://34.134.67.180:3306/airline-database'
USERNAME = 'airline-database'
PASSWORD = 'pXlZb?L%;[avj++x'
TABLE_NAME = 'Flight'

parser = argparse.ArgumentParser()
parser.add_argument("--project_id", help="Your GCP project ID", required=True)
parser.add_argument("--input_subscription", help="Input PubSub subscription", required=True)
parser.add_argument("--output_table", help="Output BigQuery table", required=True)
known_args, pipeline_args = parser.parse_known_args()

pipeline_options = PipelineOptions(pipeline_args, streaming=True)
pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id

def run(input_subscription, output_table):

    import apache_beam as beam

    with beam.Pipeline(options=pipeline_options) as p:
        messages = (
            p
            | "Read from Pub/Sub" >> ReadFromPubSub(subscription=input_subscription)
            | "Decode JSON messages" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
            | "Log Data" >> beam.Map(lambda element: logging.info(f"Processing: {element}") or element)
        )

        messages | "Write to BigQuery" >> WriteToBigQuery(
            output_table,
            schema=SCHEMA,
            create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=BigQueryDisposition.WRITE_APPEND,
            additional_bq_parameters={'timePartitioning': {'type': 'DAY'}}
        )

        def to_jdbc_row(element):

            import datetime

            return beam.Row(
                Flight_ID=str(element['Flight_ID']),  # Ensure type conversion if necessary
                flight_status=str(element['Flight_Status']),
                aircraft_id=str(element['Aircraft_ID']),
                model_id=str(element['Model_ID']),
                destination_airport=str(element['Destination_airport']),
                departure_airport=str(element['Departure_airport']),
                departure_time=str(element['Departure_Time']),
                arrival_time=str(element['Arrival_Time']),
                passport_no=str(element['Passport_No']),
                seat_no=int(element['Seat_No'])  # Ensure type conversion if necessary
            )

        messages | "Convert to JDBC Row" >> beam.Map(to_jdbc_row) | "Write to Cloud SQL" >> WriteToJdbc(
            table_name=TABLE_NAME,
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url=JDBC_URL,
            username=USERNAME,
            password=PASSWORD
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(known_args.input_subscription, known_args.output_table)
