import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, SetupOptions
from apache_beam import Pipeline
from apache_beam.transforms.periodicsequence import PeriodicImpulse
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms import ParDo, Map, WindowInto
from apache_beam.io.jdbc import WriteToJdbc
from datetime import timedelta
import random
from faker import Faker

faker = Faker()


# Options class for pipeline
class Options(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--mysql_url', type=str)
        parser.add_value_provider_argument('--mysql_table', type=str)


# Helper functions and DoFn
def adjust_weights(base_weights, variance=0.05):
    adjusted_weights = [max(0, w + random.uniform(-variance, variance)) for w in base_weights]
    total = sum(adjusted_weights)
    return [w / total for w in adjusted_weights]


class GenerateFlightData(beam.DoFn):
    def process(self, element, **kwargs):
        flight_id = faker.unique.bothify(text='??###', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        flight_status_choices = ['Cancelled', 'Delayed', 'Boarding', 'Landed', 'En Route']
        base_weights = [0.05, 0.10, 0.175, 0.175, 0.50]
        flight_status_weights = adjust_weights(base_weights, variance=0.02)
        flight_status = random.choices(flight_status_choices, weights=flight_status_weights, k=1)[0]
        aircraft_id = faker.unique.bothify(text='N####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        departure_airport = random.choice(['JFK', 'LAX', 'ORD', 'ATL'])  # Example airports
        destination_airport = random.choice(['DXB', 'LHR', 'HND', 'CDG'])  # Example airports
        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=random.randint(1, 12))

        yield {
            'Flight_ID': flight_id,
            'Flight_Status': flight_status,
            'aircraft_ID': aircraft_id,
            'Destination_airport': destination_airport,
            'Departure_airport': departure_airport,
            'Departure_Time': departure_time.isoformat(),
            'Arrival_Time': arrival_time.isoformat(),
            'Passport_No': faker.unique.bothify(text='??######'),  # Generate passport no
            'Seat_No': random.randint(1, 150)  # Assume 150 seats
        }


# Set up pipeline options
options = PipelineOptions()
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'data-systems-assignment'
# google_cloud_options.region = 'us'
google_cloud_options.staging_location = 'gs://airline-database-bucket/staging'
google_cloud_options.temp_location = 'gs://airline-database-bucket/temp'
options.view_as(SetupOptions).save_main_session = True


class PeriodicImpulse(DoFn):
    def process(self, element):
        # Emit an element every 10 seconds
        time.sleep(10)
        yield time.time()

# Define the pipeline
with Pipeline(options=options) as p:
    # Simulate data generation and streaming
    (p
     | 'Periodic Impulse' >> PeriodicImpulse(interval=timedelta(seconds=10))
     | 'Generate Flight Data' >> ParDo(GenerateFlightData())
     | 'Write to MySQL' >> WriteToJdbc(
                table_name=options.view_as(Options).mysql_table.get(),
                driver_class_name='com.mysql.cj.jdbc.Driver',
                jdbc_url=options.view_as(Options).mysql_url.get(),
                username='airline-database',  # Specify the username
                password='pXlZb?L%;[avj++x'  # Specify the password
            )
     )
