import pandas as pd

airports_df = pd.read_csv('airports.csv')
runways_df = pd.read_csv('runways.csv')
filtered_airport_codes_df = pd.read_csv('filtered_airport_codes.csv')

merged_airports_df = pd.merge(filtered_airport_codes_df[['iata_code']], airports_df[['id', 'iata_code']], on='iata_code', how='left')

runways_count_df = runways_df.groupby('airport_ref').size().reset_index(name='runway_count')

final_df = pd.merge(merged_airports_df, runways_count_df, left_on='id', right_on='airport_ref', how='left')

final_df = final_df[['iata_code', 'runway_count']]

final_csv_path = 'airport_runways_count.csv'
final_df.to_csv(final_csv_path, index=False)

print(final_df.count())
