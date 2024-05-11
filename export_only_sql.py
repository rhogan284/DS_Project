import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, DebugOptions
from apache_beam.io import ReadFromPubSub, WriteToBigQuery, BigQueryDisposition
from apache_beam.io.jdbc import WriteToJdbc
from apache_beam.transforms.window import FixedWindows

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

logging.getLogger().setLevel(logging.DEBUG)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config['google_credentials']

SCHEMA = '''
Flight_ID:STRING, Flight_Status:STRING, Aircraft_ID:STRING,
Destination_Airport:STRING, Departure_Airport:STRING,
Departure_Time:TIMESTAMP, Arrival_Time:TIMESTAMP,
Passport_No:STRING, Model_ID:STRING, Seat_No:INTEGER, Citizenship:STRING
'''

def to_flight_row(element):
    return beam.Row(
        Flight_ID=str(element['Flight_ID']),
        Flight_Status=str(element['Flight_Status']),
        Aircraft_ID=str(element['Aircraft_ID']),
        Destination_Airport=str(element['Destination_airport']),
        Departure_Airport=str(element['Departure_airport']),
        Departure_Time=str(element['Departure_Time']),
        Arrival_Time=str(element['Arrival_Time']),
        Model_ID=str(element['Model_ID'])
    )

def to_ticket_row(element):
    return beam.Row(
        Passport_No=str(element['Passport_No']),
        Citizenship=str(element['Citizenship']),
        Seat_No=int(element['Seat_No']),
        Flight_ID=str(element['Flight_ID']),
    )

def run_pipeline(input_subscription, flight_table, ticket_table):
    import apache_beam as beam
    pipeline_options = PipelineOptions(pipeline_args, streaming=True, streaming_engine_option='DATA_FLOW_SERVICE')
    pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id

    with beam.Pipeline(options=pipeline_options) as p:
        messages = (
                p
                | "Read from Pub/Sub" >> ReadFromPubSub(subscription=input_subscription)
                | "Log Data" >> beam.Map(lambda x: logging.info(f"Writing Flight Data: {x}") or x)
                | "Decode JSON messages" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
        )

    windowed_messages = messages | "Apply Windowing" >> beam.WindowInto(FixedWindows(30))

    flight_data = (
            windowed_messages
            | "Extract Flight Data" >> beam.Map(to_flight_row)
            | "Deduplicate Flight Data" >> beam.Distinct()
    )

    flight_data | "Log Flight Data" >> beam.Map(lambda x: logging.info(f"Writing Flight Data: {x}") or x)

    flight_data | "Write Flight Data to Cloud SQL" >> WriteToJdbc(
        table_name=flight_table,
        driver_class_name='com.mysql.cj.jdbc.Driver',
        jdbc_url=config['jdbc_url'],
        username=config['db_username'],
        password=config['db_password'],
    )

    ticket_data = (windowed_messages | "Extract Ticket Data" >> beam.Map(to_ticket_row))
    ticket_data_delayed = ticket_data | "Apply Ticket Windowing" >> beam.WindowInto(FixedWindows(70))

    ticket_data_delayed | "Log Ticket Data" >> beam.Map(lambda x: logging.info(f"Writing Ticket Data: {x}") or x)

    ticket_data_delayed | "Write Ticket Data to Cloud SQL" >> WriteToJdbc(
        table_name=ticket_table,
        driver_class_name='com.mysql.cj.jdbc.Driver',
        jdbc_url=config['jdbc_url'],
        username=config['db_username'],
        password=config['db_password']
    )


if __name__ == "__main__":
    import apache_beam as beam

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="Your GCP project ID", required=True)
    parser.add_argument("--input_subscription", help="Input PubSub subscription", required=True)
    parser.add_argument("--flight_table", help="MySQL table for flight details", required=True)
    parser.add_argument("--ticket_table", help="MySQL table for ticket details", required=True)
    known_args, pipeline_args = parser.parse_known_args()

    run_pipeline(known_args.input_subscription, known_args.flight_table, known_args.ticket_table)
