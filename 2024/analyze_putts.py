import matplotlib.pyplot as plt
import pandas as pd
import ast
import numpy as np
import sqlite3
from utils import geo

# Load data from SQLite
connection = sqlite3.connect("./data/10-28.sqlite3")
putts = pd.read_sql_query("SELECT * FROM round_putt", connection)
connection.close()

putts = putts[putts.distance != 0] # Clean 0 vals

putts.sort_values(by=['rnd_id', 'hole_id', 'stroke_number'])
putts['made'] = putts.groupby(['rnd_id', 'hole_id'])['stroke_number'].transform('max') == putts['stroke_number']
putts[['rnd_id', 'hole_id', 'stroke_number', 'distance', 'made']].to_csv('exports/putts.csv', index=True)

# Calculate % chance of making a putt for each distance
make_likelihoods = (
    putts.groupby('distance')
    .agg(
        Total=('distance', 'size'),                  # Total number of putts
        Made=('made', 'sum')                        # Total number of putts made
    )
    .reset_index()                                  # Reset index to make 'distance' a column
)

# Calculate make percentage
make_likelihoods['Make %'] = (make_likelihoods['Made'] / make_likelihoods['Total']) * 100

# Rename distance column for clarity (optional)
make_likelihoods.rename(columns={'distance': 'Distance'}, inplace=True)


# Convert % Chance to percentage format
# distance_likelihoods['% Chance'] *= 100

# Save distance likelihoods to a CSV file
make_likelihoods.to_csv('exports/make_likelihoods.csv', index=False)
make_likelihoods = make_likelihoods[make_likelihoods['Distance'] <= 25]

plt.figure(figsize=(10, 6))
plt.plot(make_likelihoods['Distance'], make_likelihoods['Make %'], marker='o', linestyle='-')

# Title and axis labels
plt.title('Likelihood of Making a Putt by Distance', fontsize=16)
plt.xlabel('Distance (units)', fontsize=14)
plt.ylabel('% Chance of Making Putt', fontsize=14)

# Custom x-ticks: Show every distance
plt.xticks(make_likelihoods['Distance'], fontsize=10)

# Annotate points with percentages
for x, y in zip(make_likelihoods['Distance'], make_likelihoods['Make %']):
    plt.text(x, y, f"{y:.1f}%", fontsize=8, ha='center', va='bottom')

# Show grid for readability
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
putts[['distance']].hist(bins=30, linewidth=1.2, edgecolor='black', color='red')
plt.grid(False)
plt.show()