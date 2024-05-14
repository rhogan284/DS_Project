import os
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from google.cloud import pubsub_v1

from pyspark.sql import SparkSession, Row, functions as F

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Other + Old Scripts/data-systems-assignment-a8059c08d52e.json"
project_id = "data-systems-assignment"
topic_id = "Airline-Database-PUBSUB"

spark = SparkSession.builder \
    .appName("Airport Management Simulation") \
    .master("local[*]") \
    .getOrCreate()

faker = Faker()

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def publish_message(message):
    data = message.encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Published {message} to {topic_path}: {future.result()}")

def adjust_weights(base_weights, variance=0.05):
    adjusted_weights = [max(0, w + random.uniform(-variance, variance)) for w in base_weights]
    total = sum(adjusted_weights)
    return [w / total for w in adjusted_weights]

def assign_aircraft():
    return aircraft_df.orderBy(F.rand()).limit(1).collect()[0]

def assign_model():
    return model_df.orderBy(F.rand()).limit(1).collect()[0]

def assign_passengers(seats_qty):
    return people_data_df.orderBy(F.rand()).limit(seats_qty).collect()


airports_csv = 'Entity Folders/Airports Entity/Airport_Entity.csv'
airport_codes_df = pd.read_csv(airports_csv)
airports = airport_codes_df['Airport_code'].dropna().unique().tolist()
primary_airport = 'SYD'

model_csv = 'Entity Folders/Airplane Model Entity/Airplane_Model_Entity.csv'
people_csv = 'Entity Folders/People Entity/People_Entity.csv'
aircraft_csv = 'Entity Folders/Aircraft Entity/Aircraft_Entity.csv'
model_df = pd.read_csv(model_csv)
people_data_df = spark.read.csv(people_csv, header=True, inferSchema=True)
aircraft_df = spark.read.csv(aircraft_csv, header=True, inferSchema=True)

def generate_flight_data():
    flight_id = faker.unique.bothify(text='??###', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    flight_status_choices = ['Cancelled', 'Delayed', 'Boarding', 'Landed', 'En Route']
    base_weights = [0.05, 0.10, 0.175, 0.175, 0.50]
    flight_status_weights = adjust_weights(base_weights, variance=0.02)
    flight_status = random.choices(flight_status_choices, weights=flight_status_weights, k=1)[0]

    aircraft_assigned = assign_aircraft()

    seats_qty = model_df.loc[model_df['Model'] == aircraft_assigned['Model_ID'], 'Passenger Capacity'].values[0]

    non_primary_airports = [code for code in airports if code != primary_airport]
    if flight_status == 'En Route':
        departure_airport = random.choice(non_primary_airports)
        destination_airport = primary_airport
    elif flight_status in ['Landed', 'Boarding']:
        departure_airport = primary_airport
        destination_airport = random.choice(non_primary_airports)
    else:
        if random.choice([True, False]):
            departure_airport = primary_airport
            destination_airport = random.choice(non_primary_airports)
        else:
            departure_airport = random.choice(non_primary_airports)
            destination_airport = primary_airport

    departure_time = datetime.now()
    arrival_time = departure_time + timedelta(hours=random.randint(1, 12))

    passengers = assign_passengers(seats_qty)

    flight_data = [
        Row(
            Flight_ID=flight_id,
            Flight_Status=flight_status,
            Aircraft_ID=aircraft_assigned['Aircraft_ID'],
            Destination_airport=destination_airport,
            Departure_airport=departure_airport,
            Departure_Time=departure_time,
            Arrival_Time=arrival_time,
            Passport_No=passenger['Passport_No'],
            Citizenship=passenger['Citizenship'],
            Seat_No=index+1
        ) for index, passenger in enumerate(passengers)
    ]

    return spark.createDataFrame(flight_data)

def generate_and_publish_flight_data():
    while True:
        flight_data_df = generate_flight_data()
        for row in flight_data_df.toJSON().collect():
            publish_message(row)
        time.sleep(120)


generate_and_publish_flight_data()