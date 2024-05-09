import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

logging.getLogger().setLevel(logging.INFO)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "data-systems-assignment-a8059c08d52e.json"

parser = argparse.ArgumentParser()
parser.add_argument("--project_id", help="Your GCP project ID", required=True)
parser.add_argument("--input_subscription", help="Input PubSub subscription", required=True)
parser.add_argument("--db_connection_string", help="Database connection string", required=True)
known_args, pipeline_args = parser.parse_known_args()

pipeline_options = PipelineOptions(pipeline_args, streaming=True)
pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id


class WriteToSQL(beam.DoFn):
    def __init__(self, db_connection_string):
        self.db_connection_string = db_connection_string

    def start_bundle(self):
        try:
            self.engine = create_engine(self.db_connection_string)
        except Exception as e:
            logging.error("Failed to create engine: {}".format(e))
            raise

    def process(self, element, **kwargs):
        try:
            with self.engine.connect() as connection:
                connection.execute(
                    "INSERT INTO flights (Flight_ID, Flight_Status, Aircraft_ID, Model_ID, Destination_Airport, Departure_Airport, Departure_Time, Arrival_Time, Passport_No, Seat_No) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (element['Flight_ID'], element['Flight_Status'], element['Aircraft_ID'], element['Model_ID'],
                     element['Destination_Airport'], element['Departure_Airport'], element['Departure_Time'],
                     element['Arrival_Time'], element['Passport_No'], element['Seat_No'])
                )
        except SQLAlchemyError as e:
            logging.error("Error executing SQL: {}".format(e))
            raise


def run(input_subscription, db_connection_string):
    with beam.Pipeline(options=pipeline_options) as p:
        messages = (
                p
                | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
                | "Decode JSON messages" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
                | "Log Data" >> beam.Map(lambda element: logging.info(f"Processing: {element}") or element)
        )

        messages | "Write to SQL Database" >> beam.ParDo(WriteToSQL(db_connection_string))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(known_args.input_subscription, known_args.db_connection_string)
