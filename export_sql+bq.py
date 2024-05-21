import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.io import ReadFromPubSub, WriteToBigQuery, BigQueryDisposition
from apache_beam.io.jdbc import WriteToJdbc

with open('Other + Old Scripts/config.json', 'r') as config_file:
    config = json.load(config_file)

logging.getLogger().setLevel(logging.INFO)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config['google_credentials']

SCHEMA_FLIGHT = '''
Flight_ID:STRING, Flight_Status:STRING, Aircraft_ID:STRING,
Destination_Airport:STRING, Departure_Airport:STRING,
Departure_Time:TIMESTAMP, Arrival_Time:TIMESTAMP
'''

SCHEMA_TICKET = '''
Passport_No:STRING, Seat_No:INTEGER, Citizenship:STRING, Flight_ID:STRING
'''

def to_flight_jdbc_row(element):
    return beam.Row(
        Flight_ID=str(element['Flight_ID']),
        flight_status=str(element['Flight_Status']),
        aircraft_id=str(element['Aircraft_ID']),
        destination_airport=str(element['Destination_airport']),
        departure_airport=str(element['Departure_airport']),
        departure_time=str(element['Departure_Time']),
        arrival_time=str(element['Arrival_Time'])
    )


def to_ticket_jdbc_row(element):
    return beam.Row(
        Passport_No=str(element['Passport_No']),
        Citizenship=str(element['Citizenship']),
        Seat_No=int(element['Seat_No']),
        Flight_ID=str(element['Flight_ID'])
    )


def run_pipeline(input_subscription, flight_table, ticket_table):
    with beam.Pipeline(options=pipeline_options) as p:
        messages = (
            p
            | "Read from Pub/Sub" >> ReadFromPubSub(subscription=input_subscription)
            | "Decode JSON messages" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
        )

        # Split the messages into flight and ticket data
        flight_data = messages | "Filter Flight Data" >> beam.Filter(lambda element: 'Flight_Status' in element)
        ticket_data = messages | "Filter Ticket Data" >> beam.Filter(lambda element: 'Passport_No' in element)

        # Write Flight Data to BigQuery
        flight_data | "Write Flight Data to BigQuery" >> WriteToBigQuery(
            flight_table,
            schema=SCHEMA_FLIGHT,
            create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=BigQueryDisposition.WRITE_APPEND,
            additional_bq_parameters={'timePartitioning': {'type': 'DAY'}}
        )

        # Convert to JDBC rows and write to Cloud SQL for Flights
        flight_data | "Convert Flight to JDBC Row" >> beam.Map(to_flight_jdbc_row) | "Write Flight to Cloud SQL" >> WriteToJdbc(
            table_name=config['flight_table_name'],
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url=config['jdbc_url'],
            username=config['db_username'],
            password=config['db_password']
        )

        # Write Ticket Data to BigQuery
        ticket_data | "Write Ticket Data to BigQuery" >> WriteToBigQuery(
            ticket_table,
            schema=SCHEMA_TICKET,
            create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=BigQueryDisposition.WRITE_APPEND,
        )

        # Convert to JDBC rows and write to Cloud SQL for Tickets
        ticket_data | "Convert Ticket to JDBC Row" >> beam.Map(to_ticket_jdbc_row) | "Write Ticket to Cloud SQL" >> WriteToJdbc(
            table_name=config['ticket_table_name'],
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
    known_args, pipeline_args = parser.parse_known_args()

    pipeline_options = PipelineOptions(pipeline_args, streaming=True, streaming_engine_option='DATAFLOW_SERVICE')
    pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id

    flight_table = "data-systems-assignment:Airport_Dataset.Flight"
    ticket_table = "data-systems-assignment:Airport_Dataset.Ticket"

    run_pipeline(known_args.input_subscription, flight_table, ticket_table)
