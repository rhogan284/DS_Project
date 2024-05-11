import numpy as np
import pandas as pd

# List of 30 airlines with geographic dispersion
airlines = [
    "American Airlines", "Delta Air Lines", "United Airlines", "Southwest Airlines",
    "Ryanair", "Lufthansa", "Air France", "British Airways", "Turkish Airlines", "Qantas",
    "Emirates", "Singapore Airlines", "Cathay Pacific", "China Southern Airlines", "ANA",
    "Japan Airlines", "Air Canada", "LATAM Airlines", "Aeroflot", "Etihad Airways",
    "KLM", "Qatar Airways", "IndiGo", "EasyJet", "Norwegian Air Shuttle",
    "Air China", "Korean Air", "Swiss International Air Lines", "Virgin Atlantic", "Iberia"
]

# Generate random fleet counts for each airline
fleet_counts = np.random.randint(50, 300, size=len(airlines))

# Create the airlines dataset
airlines_df = pd.DataFrame({
    "Airline_Name": airlines,
    "Aircraft_Count": fleet_counts
})

print(airlines_df.head(30))

airlines_df.to_csv('Airline_Entity.csv', index=False)