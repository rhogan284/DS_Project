import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.io import ReadFromPubSub, WriteToBigQuery, BigQueryDisposition
from apache_beam.io.jdbc import WriteToJdbc

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

logging.getLogger().setLevel(logging.INFO)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config['google_credentials']

SCHEMA = '''
Flight_ID:STRING, Flight_Status:STRING, Aircraft_ID:STRING,
Destination_Airport:STRING, Departure_Airport:STRING,
Departure_Time:TIMESTAMP, Arrival_Time:TIMESTAMP,
Passport_No:STRING, Model_ID:STRING, Seat_No:INTEGER, Citizenship:STRING
'''

def to_jdbc_row(element):
    return beam.Row(
        Flight_ID=str(element['Flight_ID']),
        flight_status=str(element['Flight_Status']),
        aircraft_id=str(element['Aircraft_ID']),
        destination_airport=str(element['Destination_airport']),
        departure_airport=str(element['Departure_airport']),
        departure_time=str(element['Departure_Time']),
        arrival_time=str(element['Arrival_Time']),
        passport_no=str(element['Passport_No']),
        model_id=str(element['Model_ID']),
        citizenship=str(element['Citizenship']),
        seat_no=int(element['Seat_No'])
    )

def run_pipeline(input_subscription, output_table):
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
        messages | "Convert to JDBC Row" >> beam.Map(to_jdbc_row) | "Write to Cloud SQL" >> WriteToJdbc(
            table_name=config['table_name'],
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url=config['jdbc_url'],
            username=config['db_username'],
            password=config['db_password']
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="Your GCP project ID", required=True)
    parser.add_argument("--input_subscription", help="Input PubSub subscription", required=True)
    parser.add_argument("--output_table", help="Output BigQuery table", required=True)
    known_args, pipeline_args = parser.parse_known_args()

    pipeline_options = PipelineOptions(pipeline_args, streaming=True, streaming_engine_option='DATA_FLOW_SERVICE')
    pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id

    run_pipeline(known_args.input_subscription, known_args.output_table)
