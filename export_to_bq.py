import argparse
import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions

# Configure logging at the INFO level
logging.getLogger().setLevel(logging.INFO)

# Set the environment variable for the Google application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "data-systems-assignment-a8059c08d52e.json"

# Schema for the BigQuery table
SCHEMA = ('Flight_ID:STRING, Flight_Status:STRING, Aircraft_ID:STRING, Model_ID:STRING, Destination_Airport:STRING, '
          'Departure_Airport:STRING, Departure_Time:TIMESTAMP, Arrival_Time:TIMESTAMP, Passport_No:STRING, '
          'Seat_No:INTEGER')

# Initialize command line argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--project_id", help="Your GCP project ID", required=True)
parser.add_argument("--input_subscription", help="Input PubSub subscription", required=True)
parser.add_argument("--output_table", help="Output BigQuery table", required=True)
known_args, pipeline_args = parser.parse_known_args()

# Set up pipeline options
pipeline_options = PipelineOptions(pipeline_args, streaming=True)
pipeline_options.view_as(GoogleCloudOptions).project = known_args.project_id

def run(input_subscription, output_table):
    with beam.Pipeline(options=pipeline_options) as p:
        # Read from Pub/Sub and process data
        messages = (
            p
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode JSON messages" >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
            | "Log Data" >> beam.Map(lambda element: logging.info(f"Processing: {element}") or element)
        )

        # Write to BigQuery
        messages | "Write to BigQuery" >> beam.io.WriteToBigQuery(
            output_table,
            schema=SCHEMA,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            additional_bq_parameters={'timePartitioning': {'type': 'DAY'}}
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(known_args.input_subscription, known_args.output_table)
