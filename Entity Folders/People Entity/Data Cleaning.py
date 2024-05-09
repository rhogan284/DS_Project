import pandas as pd

file_path = 'countries_iso3166b.csv'

df = pd.read_csv(file_path, encoding='unicode_escape')

filtered_df = df[(df['iso3'].notnull())]

final_df = filtered_df[['iso3', 'country']]

output_file_path = 'filtered_country_codes.csv'
final_df.to_csv(output_file_path, index=False)
