from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd

faker = Faker()

file_path = 'filtered_airport_codes.csv'
airport_codes_df = pd.read_csv(file_path)
airports = airport_codes_df['iata_code'].dropna().unique().tolist()

flight_entity = []

def adjust_weights(base_weights, variance=0.05):
    adjusted_weights = [max(0, w + random.uniform(-variance, variance)) for w in base_weights]
    total = sum(adjusted_weights)
    return [w / total for w in adjusted_weights]

def generate_flight_record():
    passport_No = faker.unique.bothify(text='??###', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    flight_status_choices = ['Cancelled', 'Delayed', 'Boarding', 'Landed', 'En Route']
    base_weights = [0.05, 0.10, 0.15, 0.15, 0.55]
    flight_status_weights = adjust_weights(base_weights, variance=0.02)
    flight_status = random.choices(flight_status_choices, weights=flight_status_weights, k=1)[0]

    aircraft_id = faker.unique.bothify(text='N####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    departure_airport = random.choice(airports)

    destination_airport = random.choice([code for code in airports if code != departure_airport])

    departure_time = faker.date_time_between(start_date="-2d", end_date="now")

    arrival_time = departure_time + timedelta(hours=random.randint(1, 12))

    return {
        'Flight_ID': flight_id,
        'Flight_Status': flight_status,
        'Aircraft_ID': aircraft_id,
        'Destination_Airport': destination_airport,
        'Departure_Airport': departure_airport,
        'Departure_Time': departure_time.strftime('%Y-%m-%d %H:%M:%S'),
        'Arrival_Time': arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
    }


for i in range(2000):
    flight_entity.append(generate_flight_record())

flight_entity = pd.DataFrame(flight_entity)
print(flight_entity.head())

flight_entity.to_csv('Flight_Entity.csv', index=False)