import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from apache_beam.io import ReadFromPubSub
from apache_beam.io.jdbc import WriteToJdbc

def run(argv=None, save_main_session=True):
    pipeline_options = PipelineOptions(argv)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    with beam.Pipeline(options=pipeline_options) as p:
        subscription = "projects/data-systems-assignment/subscriptions/Airline-Database-PUBSUB-sub"
        messages = (
            p
            | 'Read from PubSub' >> ReadFromPubSub(subscription=subscription)
            | 'Decode' >> beam.Map(lambda x: x.decode('utf-8'))
        )

        messages | 'Write to MySQL' >> WriteToJdbc(
            table_name='Flight',
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url='jdbc:mysql://34.134.67.180:3306/airline-database',
            username='airline-database',
            password='pXlZb?L%;[avj++x',
            statement='INSERT INTO your_table (column_name) VALUES (?)',
            driver_jars=None,
            # expansion_service='localhost:8097',  # Assuming expansion service is running on localhost:8097
            classpath=None  # Add path to your MySQL JDBC driver jar here if not in default classpath
        )


if __name__ == '__main__':
    import sys
    run(sys.argv)
