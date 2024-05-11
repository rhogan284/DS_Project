import random
from datetime import datetime
import pandas as pd

airlines_csv = 'Airline_Entity.csv'
airlines_df = pd.read_csv(airlines_csv)
model_csv = 'Airplane_Model_Entity.csv'
model_data = pd.read_csv(model_csv)

def random_date(start, end):
    return start + (end - start) * random.random()


aircraft_details = []
aircraft_id = 1
model_ids = model_data['Model'].tolist()

for index, row in airlines_df.iterrows():
    for _ in range(row['Aircraft_Count']):
        airline = row['Airline_Name']
        model_id = random.choice(model_ids)
        manufacture_date = random_date(datetime(1995, 1, 1), datetime(2022, 12, 31)).strftime('%Y-%m-%d')

        # Append each aircraft's details to the list
        aircraft_details.append({
            "Aircraft_ID": f"AC{aircraft_id:05d}",
            "Airline_Name": airline,
            "Model_ID": model_id,
            "Manufactured_Date": manufacture_date
        })
        aircraft_id += 1

# Convert the list to a DataFrame
aircraft_df = pd.DataFrame(aircraft_details)

print(aircraft_df.head(30))

aircraft_df.to_csv('Aircraft_Entity.csv', index=False)
