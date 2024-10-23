import pandas as pd
import ast
import numpy as np
import sqlite3
from utils import geo

# Load data from SQLite
connection = sqlite3.connect("./data/db.sqlite3")
og_courses = pd.read_sql_query("SELECT * FROM course_course", connection)
og_course_tees = pd.read_sql_query("SELECT * FROM course_tee", connection)
og_course_holes = pd.read_sql_query("SELECT * FROM course_hole", connection)
og_rounds = pd.read_sql_query("SELECT * FROM round_round", connection)
og_round_stats = pd.read_sql_query("SELECT * FROM round_holestats", connection)
og_strokes = pd.read_sql_query("SELECT * FROM round_stroke", connection)
og_putts = pd.read_sql_query("SELECT * FROM round_putt", connection)
connection.close()

# Clean Rounds (Only take rounds with 18 hole scores)
og_rounds.drop(og_rounds[og_rounds.holes_completed != 18].index, inplace=True)

# Get Score
## here please
def parse_coordinates(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str)

def parse_coordinates_with_parentheses(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str[1:-1])


# Apply the function to both 'start_coordinate' and 'end_coordinate' columns
og_strokes['start_coordinate'] = og_strokes['start_coordinate'].apply(parse_coordinates)
og_strokes['end_coordinate'] = og_strokes['end_coordinate'].apply(parse_coordinates)

# Calculate the distance, returning 0 if any coordinate is None
og_strokes['distance'] = og_strokes.apply(
    lambda row: 0 if row['start_coordinate'] is None or row['end_coordinate'] is None
    else geo.get_distance_between_points_yards(
        row['start_coordinate'][0], row['start_coordinate'][1],  # start lat, long
        row['end_coordinate'][0], row['end_coordinate'][1]       # end lat, long
    ), axis=1
)

og_course_holes['center_green_point'] = og_course_holes['center_green_point'].apply(parse_coordinates_with_parentheses)
og_strokes = pd.merge(og_strokes, og_course_holes[['id' 'center_green_point']], left_on='hole_id', right_on='id', how='left')
# Now calculate the distance from start_coordinate to center_green_point (the green center)
og_strokes['distance_start_to_green_center'] = og_strokes.apply(
    lambda row: 0 if row['start_coordinate'] is None or row['center_green_point'] is None
    else geo.get_distance_between_points_yards(
        row['start_coordinate'][0], row['start_coordinate'][1],  # start lat, long
        row['center_green_point'][0], row['center_green_point'][1]  # green center lat, long
    ), axis=1
)

print(og_strokes.columns)

# Clean up by dropping the extra 'id' column if needed
og_strokes.drop(columns=['id_y'], inplace=True)

strokes_per_round = og_strokes.groupby('rnd_id').size().reset_index(name='num_strokes')
putts_per_round = og_putts.groupby('rnd_id').size().reset_index(name='num_putts')
penalties_per_round = og_strokes.where(og_strokes['penalty'] == True).groupby('rnd_id').size().reset_index(name='num_penalties')
gir_per_round = og_round_stats.where(og_round_stats['gir'] == True).groupby('rnd_id').size().reset_index(name='num_gir')
gld_per_round = og_round_stats.where(og_round_stats['gld'] == True).groupby('rnd_id').size().reset_index(name='num_gld')
shots_inside_110 = og_strokes.where(og_strokes['distance_start_to_green_center'] <= 110.0).groupby('rnd_id').size().reset_index(name='num_110')
drives = og_strokes[og_strokes['club'] == 'D']
avg_drive_distance_per_round = drives.groupby('rnd_id')['distance'].mean().reset_index(name='avg_drive_distance')

# Merge this with the og_rounds DataFrame to include round details
new_rounds = pd.merge(og_rounds, strokes_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, putts_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, penalties_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gir_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gld_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, shots_inside_110, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, avg_drive_distance_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication
# new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, og_courses, left_on='course_id', right_on='id', how='left')
new_rounds.drop(columns='course_id', inplace=True)


# Fill NaN values with 0 if some rounds don't have any putts
new_rounds['num_putts'].fillna(0, inplace=True)
new_rounds.sort_values(by='date_played', inplace=True, ascending=False)

print(new_rounds[['course_id', 'date_played', 'num_strokes', 'num_putts', 'num_penalties', 'num_gir', 'num_gld', 'num_110', 'avg_drive_distance']].head(10))
og_strokes.sort_values(by='id_x', inplace=True, ascending=False)
print(og_strokes[['hole_id', 'club', 'distance', 'distance_start_to_green_center']].head(50))
print(f"Average putts: {np.mean(new_rounds[['num_putts']])}")

new_rounds[['course_id', 'date_played', 'num_strokes', 'num_putts', 'num_penalties', 'num_gir', 'num_gld', 'num_110', 'avg_drive_distance']].to_csv('exports/2024.csv', index=True)
# Get # Putts

# Get GIR

# Get GLD

# Get % Scrambling

# Get # penalties

# Get # Shots inside 110 yards

# Avg Driving Distance

# Feet of Putts

# Round Strokes
# Cum. stroke

# Round putts
