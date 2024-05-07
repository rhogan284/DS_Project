import pandas as pd

file_path = 'airport-codes_csv.csv'

airports_df = pd.read_csv(file_path)

filtered_airports_df = airports_df[(airports_df['iata_code'].notnull()) & (airports_df['iata_code'] != '0')]

final_airports_df = filtered_airports_df[['type', 'name', 'iso_country', 'iata_code']]

output_file_path = 'filtered_airport_codes.csv'
final_airports_df.to_csv(output_file_path, index=False)
