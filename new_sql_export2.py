import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io import ReadFromPubSub
from apache_beam.io.jdbc import WriteToJdbc
import json

class MyOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--input_subscription', type=str, help='Input PubSub subscription')
        parser.add_value_provider_argument('--jdbc_url', type=str, help='JDBC connection URL')
        parser.add_value_provider_argument('--db_table', type=str, help='Database table name')

def parse_json_message(message):
    """ Parses JSON message into a dictionary. """
    record = json.loads(message)
    return {
        'Flight_ID': record['Flight_ID'],
        'Flight_Status': record['Flight_Status'],
        'Aircraft_ID': record['Aircraft_ID'],
        'Model_ID': record['Model_ID'],
        'Destination_airport': record['Destination_airport'],
        'Departure_airport': record['Departure_airport'],
        'Departure_Time': record['Departure_Time'],
        'Arrival_Time': record['Arrival_Time'],
        'Passport_No': record['Passport_No'],
        'Seat_No': record['Seat_No']
    }

def run():
    options = MyOptions()
    with beam.Pipeline(options=options) as p:
        messages = (
            p
            | "Read from PubSub" >> ReadFromPubSub(subscription=options.input_subscription.get())
            | "Decode" >> beam.Map(lambda x: x.decode('utf-8'))
            | "Parse JSON" >> beam.Map(parse_json_message)
        )

        # Write to MySQL
        messages | "Write to MySQL" >> WriteToJdbc(
            table_name=options.db_table.get(),
            driver_class_name='com.mysql.jdbc.Driver',
            jdbc_url=options.jdbc_url.get(),
            username='airline-database',
            password='pXlZb?L%;[avj++x',  # Replace with actual password
            statement='''
                INSERT INTO your_table (
                    Flight_ID, Flight_Status, Aircraft_ID, Model_ID, Destination_airport, 
                    Departure_airport, Departure_Time, Arrival_Time, Passport_No, Seat_No
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            connection_properties={"useSSL": "false"}
        )

if __name__ == '__main__':
    run()
