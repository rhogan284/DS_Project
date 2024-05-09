from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd

faker = Faker()

file_path = 'filtered_country_codes.csv'
country_codes_df = pd.read_csv(file_path)
countries = country_codes_df['iso3'].dropna().unique().tolist()

people_entity = []

def adjust_weights(base_weights, variance=0.05):
    adjusted_weights = [max(0, w + random.uniform(-variance, variance)) for w in base_weights]
    total = sum(adjusted_weights)
    return [w / total for w in adjusted_weights]

def generate_person_record():
    first_name = faker.first_name()
    last_name = faker.last_name()
    dob = faker.date_of_birth(minimum_age=0, maximum_age=104).strftime('%Y-%m-%d')
    citizenship = random.choice(countries)
    passport_no = faker.bothify(text='??########????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    return {
        'First_Name': first_name,
        'Last_Name': last_name,
        'DOB': dob,
        'Citizenship': citizenship,
        'Passport_No': passport_no,
    }


for i in range(20000):
    people_entity.append(generate_person_record())

people_entity = pd.DataFrame(people_entity)
print(people_entity.head())

people_entity.to_csv('People_Entity.csv', index=False)