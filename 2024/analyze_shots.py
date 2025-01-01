import matplotlib.pyplot as plt
import pandas as pd
import ast
import numpy as np
import sqlite3
from utils import geo

# Load data from SQLite
connection = sqlite3.connect("./data/10-28.sqlite3")
strokes = pd.read_sql_query("SELECT * FROM round_stroke", connection)
connection.close()

def parse_coordinates(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str)

def parse_coordinates_with_parentheses(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str[1:-1])

def distance_from_coords(row):
    if row['start_coordinate'] is None or row['end_coordinate'] is None:
        return 0
    
    return geo.get_distance_between_points_yards(
        row['start_coordinate'][0], row['start_coordinate'][1],
        row['end_coordinate'][0], row['end_coordinate'][1]
    )


# Apply the function to both 'start_coordinate' and 'end_coordinate' columns
strokes['start_coordinate'] = strokes['start_coordinate'].apply(parse_coordinates)
strokes['end_coordinate'] = strokes['end_coordinate'].apply(parse_coordinates)

# Calculate the distance, returning 0 if any coordinate is None
strokes['distance'] = strokes.apply(distance_from_coords, axis=1)

print(strokes.head())

seven_irons = strokes.where(strokes['club'] == '7')
eight_irons = strokes.where(strokes['club'] == '8')
seven_irons[['distance']].hist(bins=20, linewidth=1.2, edgecolor='black', color='red')
print(seven_irons[['distance']].describe())
print(eight_irons[['distance']].describe())
plt.grid(False)
plt.show()