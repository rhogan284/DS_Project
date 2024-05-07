import pandas as pd

filtered_airport_codes_df = pd.read_csv('filtered_airport_codes.csv')
airport_runways_count_df = pd.read_csv('airport_runways_count.csv')

merged_df = pd.merge(filtered_airport_codes_df, airport_runways_count_df, on='iata_code', how='inner')

merged_df['timezone'] = 'TBD'

airport_entity_df = merged_df[['iata_code', 'name', 'iso_country', 'runway_count', 'timezone']]

airport_entity_df.columns = ['Airport_code', 'Airport_Name', 'Country', 'Runway_Count', 'Timezone']

airport_entity_df.to_csv('Airport_Entity.csv', index=False)
